package lexfo.scalpel;

import burp.api.montoya.MontoyaApi;
import burp.api.montoya.http.HttpService;
import burp.api.montoya.http.message.HttpMessage;
import burp.api.montoya.http.message.HttpRequestResponse;
import burp.api.montoya.http.message.requests.HttpRequest;
import burp.api.montoya.http.message.responses.HttpResponse;
import burp.api.montoya.ui.Selection;
import burp.api.montoya.ui.editor.extension.EditorCreationContext;
import burp.api.montoya.ui.editor.extension.ExtensionProvidedHttpRequestEditor;
import burp.api.montoya.ui.editor.extension.ExtensionProvidedHttpResponseEditor;
import java.awt.Component;
import java.lang.reflect.Constructor;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.swing.JTabbedPane;
import javax.swing.UIManager;
import javax.swing.plaf.basic.BasicTabbedPaneUI;
import lexfo.scalpel.ScalpelExecutor.CallableData;
import lexfo.scalpel.editors.AbstractEditor;
import lexfo.scalpel.editors.IMessageEditor;
import lexfo.scalpel.editors.ScalpelBinaryEditor;
import lexfo.scalpel.editors.ScalpelDecimalEditor;
import lexfo.scalpel.editors.ScalpelHexEditor;
import lexfo.scalpel.editors.ScalpelOctalEditor;
import lexfo.scalpel.editors.ScalpelRawEditor;

// https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/ui/editor/extension/ExtensionProvidedHttpRequestEditor.html
// https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/ui/editor/extension/ExtensionProvidedHttpResponseEditor.html
/**
  Provides an UI text editor component for editing HTTP requests or responses.
  Calls Python scripts to initialize the editor and update the requests or responses.
*/
public class ScalpelEditorTabbedPane
	implements
		ExtensionProvidedHttpRequestEditor,
		ExtensionProvidedHttpResponseEditor {

	/**
		The editor swing UI component.
	*/
	private final JTabbedPane pane = new JTabbedPane();
	/**
		The HTTP request or response being edited.
	*/
	private HttpRequestResponse _requestResponse;

	/**
		The Montoya API object.
	*/
	private final MontoyaApi API;

	/**
		The editor creation context.
	*/
	private final EditorCreationContext ctx;

	/**
		The editor type (REQUEST or RESPONSE).
	*/
	private final EditorType type;

	/**
		The editor ID. (unused)
	*/
	private final String id;

	/**
		The editor provider that instantiated this editor. (unused)
	*/
	private final ScalpelEditorProvider provider;

	/**
		The executor responsible for interacting with Python.
	*/
	private final ScalpelExecutor executor;

	private final ArrayList<IMessageEditor> editors = new ArrayList<>();

	/**
		req_edit_ or res_edit
	 */
	private final String hookPrefix;

	/**
		req_edit_in_<tab_name> or res_edit_in_<tab_name>
	 */
	private final String hookInPrefix;

	/**
		req_edit_out_<tab_name> or res_edit_out_<tab_name>
	 */
	private final String hookOutPrefix;

	/**
		Constructs a new Scalpel editor.
		
		@param API The Montoya API object.
		@param creationContext The EditorCreationContext object containing information about the editor.
		@param type The editor type (REQUEST or RESPONSE).
		@param provider The ScalpelEditorProvider object that instantiated this editor.
		@param executor The executor to use.
	*/
	ScalpelEditorTabbedPane(
		MontoyaApi API,
		EditorCreationContext creationContext,
		EditorType type,
		ScalpelEditorProvider provider,
		ScalpelExecutor executor
	) {
		// Keep a reference to the Montoya API
		this.API = API;

		// Associate the editor with an unique ID (obsolete)
		this.id = UUID.randomUUID().toString();

		// Keep a reference to the provider.
		this.provider = provider;

		// Store the context (e.g.: Tool origin, HTTP message type,...)
		this.ctx = creationContext;

		// Reference the executor to be able to call Python callbacks.
		this.executor = executor;

		// Set the editor type (REQUEST or RESPONSE).
		this.type = type;

		this.hookPrefix =
			(
				type == EditorType.REQUEST
					? Constants.REQ_EDIT_PREFIX
					: Constants.RES_EDIT_PREFIX
			);

		// req_edit_in / res_edit_in
		this.hookInPrefix = this.hookPrefix + Constants.IN_SUFFIX;
		// req_edit_out / res_edit_out
		this.hookOutPrefix = this.hookPrefix + Constants.OUT_SUFFIX;

		try {
			this.recreateEditors();
			ScalpelLogger.debug(
				"Successfully initialized ScalpelProvidedEditor for " +
				type.name()
			);
		} catch (Throwable e) {
			// Log the stack trace.
			ScalpelLogger.error("Couldn't instantiate new editor:");
			ScalpelLogger.logStackTrace(e);

			// Throw the error again.
			throw new RuntimeException(e);
		}
	}

	private int getTabNameOffsetInHookName(String hookName) {
		return hookName.startsWith(hookInPrefix)
			? hookInPrefix.length()
			: hookOutPrefix.length();
	}

	private String getHookSuffix(String hookName) {
		return hookName
			.substring(getTabNameOffsetInHookName(hookName))
			.replaceFirst("^_", "");
	}

	private String getHookPrefix(String hookName) {
		return hookName.substring(0, getTabNameOffsetInHookName(hookName));
	}

	public static final Map<String, Class<? extends AbstractEditor>> modeToEditorMap = Map.of(
		"raw",
		ScalpelRawEditor.class,
		"hex",
		ScalpelHexEditor.class,
		"octal",
		ScalpelOctalEditor.class,
		"decimal",
		ScalpelDecimalEditor.class,
		"binary",
		ScalpelBinaryEditor.class
	);

	/**
	 * A tab can be associated with at most two hooks
	 * (e.g req_edit_in and req_edit_out)
	 *
	 * This stores the informations related to only one hook and is later merged with the second hook information into a HookTabInfo
	 */
	private record PartialHookTabInfo(
		String name,
		String mode,
		String direction
	) {}

	/**
	 * This stores all the informations required to create a tab.
	 * .directions contains the whole prefix and not just "in" or "out"
	 */
	private record HookTabInfo(
		String name, // for req_edit_in_tab1 -> tab1
		String mode, // hex / raw
		Set<String> directions // re[qs]_edit_in / re[qs]_edit_out
	) {}

	private List<CallableData> getCallables() {
		// List Python callbacks.
		try {
			return executor.getCallables();
		} catch (RuntimeException e) {
			// This will fail if the script is invalid or empty.
			ScalpelLogger.trace(
				"recreateEditors(): Could not call get_callables"
			);
			ScalpelLogger.trace(e.toString());
			return null;
		}
	}

	/**
	 * Retain hooks for editing a request / response and parses them.
	 * @param callables All the Python callable objects that were found.
	 * @return Parsed hook infos
	 */
	private Stream<PartialHookTabInfo> filterEditorHooks(
		List<CallableData> callables
	) {
		return callables
			.parallelStream()
			.filter(c ->
				c.name().startsWith(this.hookInPrefix) ||
				c.name().startsWith(this.hookOutPrefix)
			)
			.map(c ->
				new PartialHookTabInfo(
					this.getHookSuffix(c.name()),
					c
						.annotations()
						.getOrDefault(
							Constants.EDITOR_MODE_ANNOTATION_KEY,
							Constants.DEFAULT_EDITOR_MODE
						),
					this.getHookPrefix(c.name())
				)
			);
	}

	/**
	 * Takes all the hooks infos and merge the corresponding ones
	 * E.g:
	 * Given the hook req_edit_in_tab1
	 * To create a tab, we need to know if req_edit_in_tab1 has a corresponding req_edit_out_tab1
	 * The editor mode (raw or hex) must be taken from the req_edit_in_tab1 annotations (@edit("hex"))
	 *
	 * @param infos The hooks individual infos.
	 * @return The hook informations required to create a Scalpel editor tab.
	 */
	private Stream<HookTabInfo> mergeHookTabInfo(
		Stream<PartialHookTabInfo> infos
	) {
		// Group the hooks individual infos by their tab name (as in req_edit_in_<tab name>)
		final Map<String, List<PartialHookTabInfo>> grouped = infos.collect(
			Collectors.groupingBy(PartialHookTabInfo::name)
		);

		// Merge the grouped individual infos into a single object.
		return grouped
			.entrySet()
			.parallelStream()
			.map(entry -> {
				final String name = entry.getKey();
				final List<PartialHookTabInfo> partials = entry.getValue();
				final Set<String> directions = partials
					.parallelStream()
					.map(PartialHookTabInfo::direction)
					.collect(Collectors.toSet());

				// Discard the "out" hook editor mode and only account for the "in" hook.
				final Optional<PartialHookTabInfo> inHook = partials
					.parallelStream()
					.filter(p -> p.direction().equals(this.hookInPrefix))
					.findFirst();

				// inHook can be empty in the case where the user specified an "out" hook
				// but not an "in" hook, which is a noop case, we handle this for safety.
				final String mode = inHook
					.map(PartialHookTabInfo::mode)
					.orElse(Constants.DEFAULT_EDITOR_MODE);

				return new HookTabInfo(name, mode, directions);
			});
	}

	/**
		Recreates the editors tabs.
		
		Calls Python to get the tabs name.
	*/
	public synchronized void recreateEditors() {
		// Destroy existing editors
		this.pane.removeAll();
		this.editors.clear();

		final List<CallableData> callables = getCallables();
		if (callables == null) {
			return;
		}

		// Retain only correct prefixes and parse hook name
		final Stream<PartialHookTabInfo> hooks = filterEditorHooks(callables);

		// Merge the individual hooks infos
		final Stream<HookTabInfo> mergedTabInfo = mergeHookTabInfo(hooks);

		// Create the editors
		mergedTabInfo.forEach(tabInfo -> {
			ScalpelLogger.debug("Creating tab for " + tabInfo);

			// Get editor implementation corresponding to mode.
			final Class<? extends AbstractEditor> dispatchedEditor = modeToEditorMap.getOrDefault(
				tabInfo.mode(),
				ScalpelRawEditor.class
			);

			final AbstractEditor editor;
			try {
				// There should be a better way to do this..
				final Constructor<? extends AbstractEditor> construcor = dispatchedEditor.getConstructor(
					String.class,
					Boolean.class,
					MontoyaApi.class,
					EditorCreationContext.class,
					EditorType.class,
					ScalpelEditorTabbedPane.class,
					ScalpelExecutor.class
				);

				editor =
					construcor.newInstance(
						tabInfo.name(),
						tabInfo.directions.contains(this.hookOutPrefix), // Read-only tab if no "out" hook.
						API,
						ctx,
						type,
						this,
						executor
					);
			} catch (Throwable ex) {
				ScalpelLogger.fatal("FATAL: Invalid editor constructor");
				// Should never happen as long as the constructor has not been overriden by an abstract declaration.
				throw new RuntimeException(ex);
			}
			ScalpelLogger.debug("Successfully created tab for " + tabInfo);

			this.editors.add(editor);

			if (
				this._requestResponse != null &&
				editor.setRequestResponseInternal(_requestResponse)
			) {
				this.addEditorToDisplayedTabs(editor);
			}
		});
	}

	/**
		Recreates the editors tabs asynchronously.
		
		Calls Python to get the tabs name.

		Might cause deadlocks or other weird issues if used in constructors directly called by Burp.
	*/
	public synchronized CompletableFuture<?> recreateEditorsAsync() {
		return Async.run(this::recreateEditors);
	}

	/**
		Returns the editor type (REQUEST or RESPONSE).

		@return The editor type (REQUEST or RESPONSE).
	*/
	public EditorType getEditorType() {
		return type;
	}

	/**
		Returns the editor's unique ID. (unused)
		@return The editor's unique ID.
	*/
	public String getId() {
		return id;
	}

	/**
		Returns the editor's creation context.
		@return The editor's creation context.
	*/
	public EditorCreationContext getCtx() {
		return ctx;
	}

	/**
		Returns the Burp editor object.
		@return The Burp editor object.
	*/
	public JTabbedPane getPane() {
		return pane;
	}

	/**
	 * Select the most suited editor for updating Burp message data.
	 *
	 * @return
	 */
	public IMessageEditor selectEditor() {
		final IMessageEditor selectedEditor = editors.get(
			pane.getSelectedIndex()
		);
		if (selectedEditor.isModified()) {
			return selectedEditor;
		}

		// TODO: Mimic burp update behaviour.
		final Stream<IMessageEditor> modifiedEditors = editors
			.stream()
			.filter(IMessageEditor::isModified);

		return modifiedEditors.findFirst().orElse(selectedEditor);
	}

	/**
	 * Returns the HTTP message being edited.
	 * @return The HTTP message being edited.
	 */
	public HttpMessage getMessage() {
		// Ensure request response exists.
		if (_requestResponse == null) {
			return null;
		}

		// Safely extract the message from the requestResponse.
		return type == EditorType.REQUEST
			? _requestResponse.request()
			: _requestResponse.response();
	}

	/**
	 *  Creates a new HTTP message by passing the editor's contents through a Python callback.
	 *
	 * @return The new HTTP message.
	 */
	private HttpMessage processOutboundMessage() {
		return selectEditor().processOutboundMessage();
	}

	/**
	 *  Creates a new HTTP request by passing the editor's contents through a Python callback.
	 * (called by Burp)
	 *
	 * @return The new HTTP request.
	 */
	@Override
	public HttpRequest getRequest() {
		ScalpelLogger.trace("getRequest called");
		// Cast the generic HttpMessage interface back to it's concrete type.
		return (HttpRequest) processOutboundMessage();
	}

	/**
	 *  Creates a new HTTP response by passing the editor's contents through a Python callback.
	 * (called by Burp)
	 *
	 * @return The new HTTP response.
	 */
	@Override
	public HttpResponse getResponse() {
		ScalpelLogger.trace("getResponse called");
		// Cast the generic HttpMessage interface back to it's concrete type.
		return (HttpResponse) processOutboundMessage();
	}

	/**
		Returns the stored HttpRequestResponse.

		@return The stored HttpRequestResponse.
	*/
	public HttpRequestResponse getRequestResponse() {
		return this._requestResponse;
	}

	/**
	 * Adds the editor to the tabbed pane
	 * If the editor caption is blank, the displayed name will be the tab index.
	 * @param editor The editor to add
	 */
	private void addEditorToDisplayedTabs(IMessageEditor editor) {
		final String displayedName;
		if (editor.caption().isBlank()) {
			// Make indexes start at 1 instead of 0
			displayedName = Integer.toString(this.pane.getTabCount() + 1);
		} else {
			displayedName = editor.caption();
		}

		final Component component = editor.uiComponent();
		pane.addTab(displayedName, component);
	}

	/**
		Sets the HttpRequestResponse to be edited.
		(called by Burp)

		@param requestResponse The HttpRequestResponse to be edited.
	*/
	@Override
	public void setRequestResponse(HttpRequestResponse requestResponse) {
		ScalpelLogger.trace("TabbedPane: setRequestResponse()");

		this._requestResponse = requestResponse;

		// Hide disabled tabs
		this.pane.removeAll();
		editors
			.parallelStream()
			.filter(e -> e.setRequestResponseInternal(requestResponse))
			.forEach(this::addEditorToDisplayedTabs);
	}

	/**
	 * Get the network informations associated with the editor
	 *
	 * Gets the HttpService from requestResponse and falls back to request if it is null
	 *
	 * @return An HttpService if found, else null
	 */
	public HttpService getHttpService() {
		final HttpRequestResponse reqRes = this._requestResponse;

		// Ensure editor is initialized
		if (reqRes == null) return null;

		// Check if networking infos are available in the requestRespone
		if (reqRes.httpService() != null) {
			return reqRes.httpService();
		}

		// Fall back to the initiating request
		final HttpRequest req = reqRes.request();
		if (req != null) {
			return req.httpService();
		}

		return null;
	}

	/**
		Determines whether the editor should be enabled for the provided HttpRequestResponse.
		Also initializes the editor with Python callbacks output of the inputted HTTP message.
		(called by Burp)

		@param requestResponse The HttpRequestResponse to be edited.
	*/
	@Override
	public boolean isEnabledFor(HttpRequestResponse requestResponse) {
		ScalpelLogger.trace("TabbedPane: isEnabledFor()");
		try {
			return editors
				.parallelStream()
				.anyMatch(e -> e.isEnabledFor(requestResponse));
		} catch (Throwable e) {
			ScalpelLogger.logStackTrace(e);
		}
		return false;
	}

	/**
		Returns the name of the tab.
		(called by Burp)

		@return The name of the tab.
	*/
	@Override
	public String caption() {
		// Return the tab name.
		return "Scalpel";
	}

	// Hide tab bar when there is only 1 tab
	private void adjustTabBarVisibility() {
		if (pane.getTabCount() == 1) {
			pane.setUI(
				new BasicTabbedPaneUI() {
					@Override
					protected int calculateTabAreaHeight(
						int tabPlacement,
						int horizRunCount,
						int maxTabHeight
					) {
						return 0;
					}
				}
			);
		} else {
			// Reset to the default UI if more than one tab is present
			UIManager.getLookAndFeel().provideErrorFeedback(pane);
			pane.updateUI();
		}
	}

	/**
		Returns the underlying UI component.
		(called by Burp)

		@return The underlying UI component.
	*/
	@Override
	public Component uiComponent() {
		adjustTabBarVisibility();
		return pane;
	}

	/**
		Returns the selected data.
		(called by Burp)

		@return The selected data.
	*/
	@Override
	public Selection selectedData() {
		return selectEditor().selectedData();
	}

	/**
		Returns whether the editor has been modified.
		(called by Burp)

		@return Whether the editor has been modified.
	*/
	@Override
	public boolean isModified() {
		return editors.stream().anyMatch(IMessageEditor::isModified);
	}
}
