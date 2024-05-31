package lexfo.scalpel;

import burp.api.montoya.MontoyaApi;
import burp.api.montoya.ui.Theme;
import com.intellij.uiDesigner.core.GridConstraints;
import com.intellij.uiDesigner.core.GridLayoutManager;
import com.intellij.uiDesigner.core.Spacer;
import com.jediterm.terminal.TtyConnector;
import com.jediterm.terminal.ui.JediTermWidget;
import com.jgoodies.forms.layout.CellConstraints;
import com.jgoodies.forms.layout.FormLayout;
import java.awt.*;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.StringSelection;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.function.Consumer;
import java.util.function.Supplier;
import javax.swing.*;
import javax.swing.border.TitledBorder;
import javax.swing.event.HyperlinkEvent;
import javax.swing.event.ListSelectionEvent;
import javax.swing.table.DefaultTableModel;
import javax.swing.text.BadLocationException;
import javax.swing.text.Document;
import lexfo.scalpel.ScalpelLogger.Level;
import lexfo.scalpel.Venv.PackageInfo;
import lexfo.scalpel.components.PlaceholderTextField;
import lexfo.scalpel.components.SettingsPanel;
import lexfo.scalpel.components.WorkingPopup;

/**
 * Burp tab handling Scalpel configuration
 * IntelliJ's GUI designer is needed to edit most components.
 */
public class ConfigTab extends JFrame {

	private JPanel rootPanel;
	private JButton frameworkBrowseButton;
	private JTextField frameworkPathField;
	private JPanel browsePanel;
	private JPanel frameworkConfigPanel;
	private JTextArea frameworkPathTextArea;
	private JPanel scriptConfigPanel;
	private JButton scriptBrowseButton;
	private JLabel scriptPathTextArea;
	private JediTermWidget terminalForVenvConfig;
	private JList<String> venvListComponent;
	private JTable packagesTable;
	private PlaceholderTextField addVentText = new PlaceholderTextField(
		"Enter a virtualenv path or name here to import or create one."
	);
	private JButton addVenvButton;
	private JPanel venvSelectPanel;
	private JButton openScriptButton;
	private JButton createButton;
	private JList<String> venvScriptList;
	private JPanel listPannel;
	private JButton openFolderButton;
	private JButton scalpelIsENABLEDButton;
	private JTextArea stderrTextArea;
	private JTextArea stdoutTextArea;
	private JTextPane helpTextPane;
	private JPanel outputTabPanel;
	private JScrollPane stdoutScrollPane;
	private JScrollPane stderrScrollPane;
	private JTextPane debugInfoTextPane;
	private JLabel selectedScriptLabel;
	private JButton resetTerminalButton;
	private JButton copyToClipboardButton;
	private JPanel settingsTab;
	private JButton openIssueOnGitHubButton;
	private final transient ScalpelExecutor scalpelExecutor;
	private final transient Config config;
	private final transient MontoyaApi API;
	private final Theme theme;
	private final Frame burpFrame;
	private final SettingsPanel settingsPanel = new SettingsPanel();

	private static ConfigTab instance = null;

	public static ConfigTab getInstance() {
		if (instance == null) {
			throw new IllegalStateException("ConfigTab was never initialized.");
		}
		return instance;
	}

	public ConfigTab(
		MontoyaApi API,
		ScalpelExecutor executor,
		Config config,
		Theme theme
	) {
		// Set the singleton instance, throw an exception if it's already set.
		if (instance != null) {
			throw new IllegalStateException(
				"More than one instance of ConfigTab is not allowed."
			);
		}

		this.config = config;
		this.scalpelExecutor = executor;
		this.theme = theme;
		this.API = API;
		this.burpFrame = API.userInterface().swingUtils().suiteFrame();

		$$$setupUI$$$();

		instance = this;
		setupVenvTab();
		setupHelpTab();
		setupLogsTab();
		setupDebugInfoTab();
		setupSettingsTab();
	}

	private void setupVenvTab() {
		// Open file browser to select the script to execute.
		scriptBrowseButton.addActionListener(e ->
			handleBrowseButtonClick(
				() -> RessourcesUnpacker.DEFAULT_SCRIPT_PATH,
				this::setAndStoreScript
			)
		);

		// Fill the venv list component.
		venvListComponent.setListData(config.getVenvPaths());

		// Update the displayed packages
		updatePackagesTable();
		updateScriptList();

		// Change the venv, terminal and package table when the user selects a venv.
		venvListComponent.addListSelectionListener(
			this::handleVenvListSelectionEvent
		);

		addListDoubleClickListener(
			venvListComponent,
			this::handleVenvListSelectionEvent
		);

		// Add a new venv when the user clicks the button.
		addVenvButton.addActionListener(__ -> handleVenvButton());

		// Add a new venv when the user presses enter in the text field.
		addVentText.addActionListener(__ -> handleVenvButton());

		openScriptButton.addActionListener(__ -> handleOpenScriptButton());

		createButton.addActionListener(__ -> handleNewScriptButton());

		openFolderButton.addActionListener(__ -> handleOpenScriptFolderButton()
		);

		this.scalpelIsENABLEDButton.addActionListener(__ -> handleEnableButton()
			);

		if (!config.isEnabled()) {
			this.scalpelIsENABLEDButton.setText("Scalpel is DISABLED");
		}

		// Implement the terminal reset button
		resetTerminalButton.addActionListener(__ -> {
			final String selectedVenvPath = config
				.getSelectedWorkspacePath()
				.toString();
			updateTerminal(selectedVenvPath);
		});

		venvScriptList.addListSelectionListener(e -> {
			if (!e.getValueIsAdjusting()) {
				this.handleScriptListSelectionEvent();
			}
		});
	}

	private void setupHelpTab() {
		// Make HTML links clickable in the help text pane.
		helpTextPane.addHyperlinkListener(e -> {
			if (HyperlinkEvent.EventType.ACTIVATED.equals(e.getEventType())) {
				try {
					Desktop.getDesktop().browse(e.getURL().toURI()); // Open link in the default browser.
				} catch (IOException | URISyntaxException ex) {
					ex.printStackTrace();
				}
			}
		});
	}

	private void setupLogsTab() {
		// For some reason IntelliJ's GUI designer doesn't let you set a simple fixed
		// GridLayout.
		// So we do it manually here.
		outputTabPanel.setLayout(new GridLayout(1, 2)); // 1 row, 2 columns

		// Adjusting autoScroll for stdoutTextArea
		UIUtils.setupAutoScroll(stdoutScrollPane, stdoutTextArea);
		// Adjusting autoScroll for stderrTextArea
		UIUtils.setupAutoScroll(stderrScrollPane, stderrTextArea);

		selectedScriptLabel.setText(
			config.getUserScriptPath().getFileName().toString()
		);
	}

	private void setupCopyButton() {
		// Implement the copy to clipboard button
		copyToClipboardButton.addActionListener(__ -> {
			final String text = debugInfoTextPane.getText();
			final Clipboard clipboard = Toolkit
				.getDefaultToolkit()
				.getSystemClipboard();

			clipboard.setContents(new StringSelection(text), null);

			// Change the button text to "Copied!" for 1s
			copyToClipboardButton.setText("Copied!");
			Async.run(() -> {
				try {
					Thread.sleep(1000);
				} catch (InterruptedException e) {
					ScalpelLogger.logStackTrace(e);
				}
				copyToClipboardButton.setText("Copy to clipboard");
			});

			// Focus the debug info text
			debugInfoTextPane.requestFocus();

			// Select the whole debug text for visual feedback
			debugInfoTextPane.selectAll();
		});
	}

	public void setSettings(Map<String, String> settings) {
		this.settingsPanel.setSettingsValues(settings);
	}

	private void setupSettingsTab() {
		this.settingsPanel.addDropdownSetting(
				"logLevel",
				"Log level",
				Level.names,
				config.getLogLevel()
			);

		this.settingsPanel.addTextFieldSetting(
				"openScriptCommand",
				"\"Open script\" button command",
				config.getOpenScriptCommand()
			);

		this.settingsPanel.addTextFieldSetting(
				"editScriptCommand",
				"Edit script in terminal command",
				config.getEditScriptCommand()
			);

		this.settingsPanel.addTextFieldSetting(
				"openFolderCommand",
				"\"Open folder\" button command",
				config.getOpenFolderCommand()
			);

		this.settingsPanel.addCheckboxSetting(
				"displayProxyErrorPopup",
				"Display error popup",
				"True".equals(config.getDisplayProxyErrorPopup())
			);

		// Padding
		this.settingsPanel.addInformationText("");
		this.settingsPanel.addInformationText("Available placeholders:");
		this.settingsPanel.addInformationText(
				"  - {file}: The absolute path to the selected script"
			);
		this.settingsPanel.addInformationText(
				"  - {dir}: The absolute path to the selected script containing directory"
			);

		this.settingsPanel.addListener(settings -> {
				ScalpelLogger.info("Settings changed: " + settings);
				final String logLevel = settings.get("logLevel");
				ScalpelLogger.setLogLevel(logLevel);
				config.setLogLevel(logLevel);
				config.setOpenScriptCommand(settings.get("openScriptCommand"));
				config.setEditScriptCommand(settings.get("editScriptCommand"));
				config.setOpenFolderCommand(settings.get("openFolderCommand"));
				config.setDisplayProxyErrorPopup(
					settings.get("displayProxyErrorPopup")
				);
			});

		this.settingsTab.add(this.settingsPanel, BorderLayout.CENTER);
	}

	private void setupGitHubIssueButton() {
		openIssueOnGitHubButton.addActionListener(__ -> {
			try {
				final String title = URLEncoder.encode(
					"Failed to install Scalpel",
					"UTF-8"
				);
				final String text = this.debugInfoTextPane.getText();

				// Truncate at 6500 chars
				final Integer maxSize = 6000;

				final String truncatedText = text.length() < maxSize
					? text
					: "/!\\ The debug report is too long to be fully included in the URL" +
					", please copy it manually from the \"Debug Info\" tab /!\\\n" +
					text.substring(0, maxSize) +
					"\n[TRUNCATED]";
				final String body = URLEncoder.encode(
					"Please describe the issue here\n\n# Debug report\n```\n" +
					truncatedText +
					"\n\n```",
					"UTF-8"
				);
				final String URL =
					"https://github.com/ambionics/scalpel/issues/new?title=" +
					title +
					"&body=" +
					body;

				Desktop.getDesktop().browse(new URI(URL));
			} catch (IOException | URISyntaxException e) {
				ScalpelLogger.logStackTrace(e);
			}
		});
	}

	private void setupDebugInfoTab() {
		setupCopyButton();
		setupGitHubIssueButton();

		final String timestamp = new SimpleDateFormat("dd-MM-yyyy HH:mm")
			.format(new Date());

		final String configDump = config.dumpConfig();
		final String pythonVersion = PythonSetup.executePythonCommand(
			"import sys; print('.'.join(map(str, sys.version_info[:3])))"
		);
		final Path jdkPath = config.getJdkPath();

		final StringBuilder out = new StringBuilder();
		out
			.append("Debug report generated on ")
			.append(timestamp)
			.append("\n\n");

		final String[] properties = {
			"os.name",
			"os.version",
			"os.arch",
			"java.version",
			"user.name",
			"user.home",
			"user.dir",
		};
		for (final String property : properties) {
			out
				.append(property)
				.append(": ")
				.append(System.getProperty(property))
				.append("\n");
		}

		out.append("Python version: ").append(pythonVersion).append("\n");
		out.append("JDK path: ").append(jdkPath).append("\n");

		out
			.append("\n------------------------\n")
			.append(configDump)
			.append("\n------------------------\n");
		out.append("Installed packages in venv:\n");

		final PackageInfo[] installedPackages;
		try {
			installedPackages =
				Venv.getInstalledPackages(config.getSelectedWorkspacePath());

			for (PackageInfo packageInfo : installedPackages) {
				out.append(
					packageInfo.name + " : " + packageInfo.version + "\n"
				);
			}
		} catch (IOException e) {
			out.append(
				ScalpelLogger.exceptionToErrorMsg(
					e,
					"Failed to get installed packages"
				)
			);
		}

		final File selectedScript = config.getUserScriptPath().toFile();
		try {
			final String content = new String(
				Files.readAllBytes(selectedScript.toPath())
			);
			out.append("\n---- Script content -----\n");
			out.append(content);
			out.append("\n------------------------\n");
		} catch (IOException e) {
			out.append(
				ScalpelLogger.exceptionToErrorMsg(
					e,
					"Failed to read script file"
				)
			);
		}

		out.append("---- Full debug log ----\n\n");
		this.debugInfoTextPane.setText(out.toString());
	}

	public static void appendToDebugInfo(String info) {
		if (instance == null) {
			return;
		}
		final JTextPane pane = instance.debugInfoTextPane;

		// Safely append text to the JTextPane
		SwingUtilities.invokeLater(() -> {
			final Document doc = pane.getDocument();
			try {
				// Append new info as a new line at the end of the Document
				doc.insertString(doc.getLength(), "\n" + info, null);
			} catch (BadLocationException e) {
				ScalpelLogger.logStackTrace(e);
			}
		});
	}

	/**
	 * Push a character to a stdout or stderr text area.
	 *
	 * @param c        The character to push.
	 * @param isStdout Whether the character is from stdout or stderr.
	 */

	public static void pushCharToOutput(int c, boolean isStdout) {
		if (instance == null) {
			return;
		}
		final JTextArea textArea = isStdout
			? instance.stdoutTextArea
			: instance.stderrTextArea;
		textArea.append(String.valueOf((char) c));
	}

	public static void putStringToOutput(String s, boolean isStdout) {
		if (instance == null) {
			return;
		}
		final JTextArea textArea = isStdout
			? instance.stdoutTextArea
			: instance.stderrTextArea;
		textArea.append(s);
		textArea.append("\n\n");
	}

	public static void clearOutputs(String msg) {
		if (instance == null) {
			return;
		}
		final String clearedTimestamp = new SimpleDateFormat("HH:mm:ss")
			.format(new Date());

		final String clearedMsg =
			"--- CLEARED at " +
			clearedTimestamp +
			" ---\n" +
			msg +
			"\n-------------------------------------------------------------------\n\n";

		instance.stdoutTextArea.setText(clearedMsg);
		instance.stderrTextArea.setText(clearedMsg);
	}

	/**
	 * JList doesn't natively support double click events, so we implment it
	 * ourselves.
	 *
	 * @param <T>
	 * @param list    The list to add the listener to.
	 * @param handler The listener handler callback.
	 */
	private <T> void addListDoubleClickListener(
		JList<T> list,
		Consumer<ListSelectionEvent> handler
	) {
		list.addMouseListener(
			new MouseAdapter() {
				@Override
				public void mouseClicked(MouseEvent evt) {
					if (evt.getClickCount() != 2) {
						// Not a double click
						return;
					}

					// Get the selected list elem from the click coordinates
					final int selectedIndex = list.locationToIndex(
						evt.getPoint()
					);

					// Convert the MouseEvent into a corresponding ListSelectionEvent
					final ListSelectionEvent passedEvent = new ListSelectionEvent(
						evt.getSource(),
						selectedIndex,
						selectedIndex,
						false
					);

					handler.accept(passedEvent);
				}
			}
		);
	}

	private void handleOpenScriptFolderButton() {
		final File script = config.getUserScriptPath().toFile();
		final File folder = script.getParentFile();
		final Map<String, String> settings = settingsPanel.getSettingsValues();
		final String command = settings.get("openFolderCommand");
		final String cmd = cmdFormat(
			command,
			folder.getAbsolutePath(),
			script.getAbsolutePath()
		);

		updateTerminal(
			config.getSelectedWorkspacePath().toString(),
			folder.getAbsolutePath(),
			cmd
		);
	}

	private void handleScriptListSelectionEvent() {
		// Get the selected script name.
		final Optional<String> selected = Optional.ofNullable(
			venvScriptList.getSelectedValue()
		);

		selected.ifPresent(s -> {
			final Path path = config
				.getSelectedWorkspacePath()
				.resolve(s)
				.toAbsolutePath();

			selectScript(path);
		});
	}

	private void updateScriptList() {
		Async.run(() -> {
			final JList<String> list = this.venvScriptList;
			final File selectedVenv = config
				.getSelectedWorkspacePath()
				.toFile();
			final File[] files = selectedVenv.listFiles(f ->
				f.getName().endsWith(".py")
			);

			final String selected = config
				.getUserScriptPath()
				.getFileName()
				.toString();

			if (files != null) {
				Arrays.sort(
					files,
					(f1, f2) -> {
						// Ensure selected script comes up on top
						if (selected.equalsIgnoreCase(f1.getName())) {
							return -1;
						} else if (selected.equalsIgnoreCase(f2.getName())) {
							return 1;
						} else {
							return f1
								.getName()
								.compareToIgnoreCase(f2.getName());
						}
					}
				);
			}

			final DefaultListModel<String> listModel = new DefaultListModel<>();

			// Fill the model with the file names
			if (files != null) {
				for (File file : files) {
					listModel.addElement(file.getName());
				}
			}

			list.setModel(listModel);
		});
	}

	private void selectScript(Path path) {
		// Select the script
		config.setUserScriptPath(path);

		// Reload the executor
		Async.run(scalpelExecutor::notifyEventLoop);

		this.selectedScriptLabel.setText(path.getFileName().toString());

		// Display the script in the terminal.
		openEditorInTerminal(path);
	}

	private void handleNewScriptButton() {
		final File venv = config.getSelectedWorkspacePath().toFile();

		// Prompt the user for a name
		String fileName = JOptionPane.showInputDialog(
			burpFrame,
			"Enter the name for the new script"
		);

		if (fileName == null || fileName.trim().isEmpty()) {
			// The user didn't enter a name
			JOptionPane.showMessageDialog(
				burpFrame,
				"You must provide a name for the file."
			);
			return;
		}

		// Append .py extension if it's not there
		if (!fileName.endsWith(".py")) {
			fileName += ".py";
		}

		// Define the source file
		Path source = Path.of(
			System.getProperty("user.home"),
			".scalpel",
			"extracted",
			"templates",
			"default.py"
		);

		// Define the destination file
		final Path destination = venv.toPath().resolve(fileName);

		// Copy the file
		try {
			Files.copy(
				source,
				destination,
				StandardCopyOption.REPLACE_EXISTING
			);
			JOptionPane.showMessageDialog(
				burpFrame,
				"File was successfully created!"
			);

			final Path absolutePath = destination.toAbsolutePath();

			selectScript(absolutePath);
			updateScriptList();
		} catch (IOException e) {
			JOptionPane.showMessageDialog(
				burpFrame,
				"Error copying file: " + e.getMessage()
			);
		}
	}

	/**
	 * Opens the script in a terminal editor
	 * <p>
	 * Tries to use the EDITOR env var
	 * Falls back to vi if EDITOR is missing
	 *
	 * @param fileToEdit
	 */
	private void openEditorInTerminal(Path fileToEdit) {
		final Path dir = config.getSelectedWorkspacePath();
		final String cmd = cmdFormat(
			config.getEditScriptCommand(),
			dir,
			fileToEdit
		);

		final String cwd = fileToEdit.getParent().toString();

		this.updateTerminal(
				config.getSelectedWorkspacePath().toString(),
				cwd,
				cmd
			);
	}

	private String cmdFormat(String fmt, Object dir, Object file) {
		return fmt
			.replace("{dir}", Terminal.escapeshellarg(dir.toString()))
			.replace("{file}", Terminal.escapeshellarg(file.toString()));
	}

	private void handleOpenScriptButton() {
		final Path script = config.getUserScriptPath();
		launchOpenScriptCommand(script);
	}

	private void launchOpenScriptCommand(Path script) {
		final Path venvDir = config.getSelectedWorkspacePath();
		final Map<String, String> settings = settingsPanel.getSettingsValues();
		final String cmdFmt = settings.get("openScriptCommand");
		final String cmd = cmdFormat(cmdFmt, venvDir, script);

		updateTerminal(
			config.getSelectedWorkspacePath().toString(),
			script.getParent().toString(),
			cmd
		);
	}

	private void handleEnableButton() {
		if (this.scalpelExecutor.isEnabled()) {
			this.scalpelIsENABLEDButton.setText("Scalpel is DISABLED");
			this.config.setEnabled(false);
			this.scalpelExecutor.disable();
		} else {
			this.scalpelIsENABLEDButton.setText("Scalpel is ENABLED");
			this.config.setEnabled(true);
			this.scalpelExecutor.enable();
		}
	}

	private void handleVenvButton() {
		final String value = addVentText.getText().trim();

		if (value.isEmpty()) {
			return;
		}

		final Path path;
		try {
			if ((new File(value).isAbsolute())) {
				// The user provided an absolute path, use it as is.
				path = Path.of(value);
			} else if (value.contains(File.separator)) {
				// The user provided a relative path, forbid it.
				throw new IllegalArgumentException(
					"Venv name cannot contain " +
					File.separator +
					"\n" +
					"Please provide a venv name or an absolute path."
				);
			} else {
				// The user provided a name, use it to create a venv in the default venvs dir.
				path =
					Paths.get(
						Workspace.getWorkspacesDir().getAbsolutePath(),
						value
					);
			}
		} catch (IllegalArgumentException e) {
			JOptionPane.showMessageDialog(
				burpFrame,
				e.getMessage(),
				"Invalid venv name or absolute path",
				JOptionPane.ERROR_MESSAGE
			);
			return;
		}

		WorkingPopup.showBlockingWaitDialog(
			"Creating venv and installing required packages...",
			label -> {
				// Clear the text field.
				addVentText.setEditable(false);
				addVentText.setText("Please wait ...");

				// Create the venv and installed required packages. (i.e. mitmproxy)
				try {
					Workspace.createAndInitWorkspace(
						path,
						Optional.of(config.getJdkPath()),
						Optional.of(terminalForVenvConfig.getTerminal())
					);

					// Add the venv to the config.
					config.addVenvPath(path);

					// Clear the text field.
					addVentText.setText("");

					// Display the venv in the list.
					venvListComponent.setListData(config.getVenvPaths());

					venvListComponent.setSelectedIndex(
						config.getVenvPaths().length - 1
					);
				} catch (RuntimeException e) {
					final String msg =
						"Failed to create venv: \n" + e.getMessage();
					ScalpelLogger.error(msg);
					ScalpelLogger.logStackTrace(e);
					JOptionPane.showMessageDialog(
						burpFrame,
						msg,
						"Failed to create venv",
						JOptionPane.ERROR_MESSAGE
					);
				}
				addVentText.setEditable(true);
			}
		);
	}

	private synchronized void updateTerminal(
		String selectedVenvPath,
		String cwd,
		String cmd
	) {
		final JediTermWidget termWidget = this.terminalForVenvConfig;
		final TtyConnector oldConnector = termWidget.getTtyConnector();

		// Close asynchronously to avoid losing time.
		termWidget.stop();
		// Kill the old process.
		oldConnector.close();

		final com.jediterm.terminal.Terminal term = termWidget.getTerminal();
		final int width = term.getTerminalWidth();
		final int height = term.getTerminalHeight();
		final Dimension dimension = new Dimension(width, height);

		// Start the process while the terminal is closing
		final TtyConnector connector = Terminal.createTtyConnector(
			selectedVenvPath,
			Optional.of(dimension),
			Optional.ofNullable(cwd),
			Optional.ofNullable(cmd)
		);

		// Connect the terminal to the new process in the new venv.
		termWidget.setTtyConnector(connector);

		term.reset();
		term.cursorPosition(0, 0);

		// Start the terminal.
		termWidget.start();
	}

	private void updateTerminal(String selectedVenvPath) {
		updateTerminal(selectedVenvPath, null, null);
	}

	private void handleVenvListSelectionEvent(ListSelectionEvent e) {
		// Ignore intermediate events.
		if (e.getValueIsAdjusting()) {
			return;
		}

		// Get the selected venv path.
		final String selectedVenvPath = venvListComponent.getSelectedValue();

		if (selectedVenvPath == null) {
			return;
		}

		config.setSelectedVenvPath(Path.of(selectedVenvPath));

		Async.run(scalpelExecutor::notifyEventLoop);

		// Update the package table.
		Async.run(this::updatePackagesTable);
		Async.run(() -> updateTerminal(selectedVenvPath));
		Async.run(this::updateScriptList);
	}

	private CompletableFuture<Void> handleBrowseButtonClick(
		Supplier<Path> getter,
		Consumer<Path> setter
	) {
		return Async.run(() -> {
			final JFileChooser fileChooser = new JFileChooser();

			// Allow the user to only select files.
			fileChooser.setFileSelectionMode(JFileChooser.FILES_ONLY);

			// Set default path to the path in the text field.
			fileChooser.setCurrentDirectory(getter.get().toFile());

			final int result = fileChooser.showOpenDialog(this);

			// When the user selects a file, set the text field to the selected file.
			if (result == JFileChooser.APPROVE_OPTION) {
				setter.accept(
					fileChooser.getSelectedFile().toPath().toAbsolutePath()
				);
			}
		});
	}

	private CompletableFuture<Void> updatePackagesTable(
		Consumer<JTable> onSuccess,
		Runnable onFail
	) {
		return Async.run(() -> {
			final PackageInfo[] installedPackages;
			try {
				installedPackages =
					Venv.getInstalledPackages(
						config.getSelectedWorkspacePath()
					);
			} catch (IOException e) {
				JOptionPane.showMessageDialog(
					burpFrame,
					"Failed to get installed packages: \n" + e.getMessage(),
					"Failed to get installed packages",
					JOptionPane.ERROR_MESSAGE
				);
				onFail.run();
				return;
			}

			// Create a table model with the appropriate column names
			final DefaultTableModel tableModel = new DefaultTableModel(
				new Object[] { "Package", "Version" },
				0
			);

			// Parse with jackson and add to the table model
			Arrays
				.stream(installedPackages)
				.map(p -> new Object[] { p.name, p.version })
				.forEach(tableModel::addRow);

			// Set the table model
			packagesTable.setModel(tableModel);

			// make the table uneditable
			packagesTable.setDefaultEditor(Object.class, null);

			onSuccess.accept(packagesTable);
		});
	}

	private void updatePackagesTable(Consumer<JTable> onSuccess) {
		updatePackagesTable(onSuccess, () -> {});
	}

	private void updatePackagesTable() {
		updatePackagesTable(__ -> {});
	}

	private void setAndStoreScript(final Path path) {
		final Path copied;
		try {
			copied =
				Workspace.copyScriptToWorkspace(
					config.getSelectedWorkspacePath(),
					path
				);
		} catch (RuntimeException e) {
			// Error popup
			JOptionPane.showMessageDialog(
				burpFrame,
				e.getMessage(),
				"Could not copy script to venv.",
				JOptionPane.ERROR_MESSAGE
			);
			return;
		}

		// Store the path in the config. (writes to disk)
		config.setUserScriptPath(copied);
		Async.run(scalpelExecutor::notifyEventLoop);

		Async.run(this::updateScriptList);
		Async.run(() -> selectScript(copied));
	}

	/**
	 * Returns the UI component to display.
	 *
	 * @return the UI component to display
	 */
	public Component uiComponent() {
		return rootPanel;
	}

	private void createUIComponents() {
		rootPanel = new JPanel();

		// Create the TtyConnector
		terminalForVenvConfig =
			Terminal.createTerminal(
				theme,
				config.getSelectedWorkspacePath().toString()
			);
	}

	/**
	 * Method generated by IntelliJ IDEA GUI Designer
	 * >>> IMPORTANT!! <<<
	 * DO NOT edit this method OR call it in your code!
	 *
	 * @noinspection ALL
	 */
	private void $$$setupUI$$$() {
		createUIComponents();
		rootPanel.setLayout(
			new GridLayoutManager(2, 3, new Insets(0, 0, 0, 0), -1, -1)
		);
		rootPanel.setBorder(
			BorderFactory.createTitledBorder(
				null,
				"",
				TitledBorder.DEFAULT_JUSTIFICATION,
				TitledBorder.DEFAULT_POSITION,
				null,
				null
			)
		);
		final JTabbedPane tabbedPane1 = new JTabbedPane();
		tabbedPane1.setToolTipText("");
		rootPanel.add(
			tabbedPane1,
			new GridConstraints(
				0,
				0,
				1,
				3,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				new Dimension(200, 200),
				null,
				0,
				false
			)
		);
		final JPanel panel1 = new JPanel();
		panel1.setLayout(
			new GridLayoutManager(1, 3, new Insets(0, 0, 0, 0), -1, -1)
		);
		tabbedPane1.addTab("Scripts and Venv", panel1);
		venvSelectPanel = new JPanel();
		venvSelectPanel.setLayout(
			new GridLayoutManager(4, 2, new Insets(5, 5, 5, 0), -1, -1)
		);
		panel1.add(
			venvSelectPanel,
			new GridConstraints(
				0,
				0,
				1,
				2,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		venvSelectPanel.setBorder(
			BorderFactory.createTitledBorder(
				null,
				"",
				TitledBorder.DEFAULT_JUSTIFICATION,
				TitledBorder.DEFAULT_POSITION,
				null,
				null
			)
		);
		final JPanel panel2 = new JPanel();
		panel2.setLayout(new BorderLayout(0, 0));
		venvSelectPanel.add(
			panel2,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_SOUTH,
				GridConstraints.FILL_HORIZONTAL,
				1,
				1,
				null,
				new Dimension(100, -1),
				null,
				0,
				false
			)
		);
		panel2.add(addVentText, BorderLayout.CENTER);
		addVenvButton = new JButton();
		addVenvButton.setText("+");
		addVenvButton.setToolTipText("Add/Create the virtualenv");
		panel2.add(addVenvButton, BorderLayout.EAST);
		terminalForVenvConfig.setToolTipText(
			"A terminal to install new packages and edit your script"
		);
		venvSelectPanel.add(
			terminalForVenvConfig,
			new GridConstraints(
				0,
				1,
				4,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		final JPanel panel3 = new JPanel();
		panel3.setLayout(
			new GridLayoutManager(3, 1, new Insets(0, 0, 0, 0), -1, -1)
		);
		venvSelectPanel.add(
			panel3,
			new GridConstraints(
				1,
				0,
				3,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		final JScrollPane scrollPane1 = new JScrollPane();
		panel3.add(
			scrollPane1,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				1,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		venvListComponent = new JList();
		final DefaultListModel defaultListModel1 = new DefaultListModel();
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("loremaucupatum");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatiolorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatiolorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatiolorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatiolorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatiolorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		defaultListModel1.addElement("lorem");
		defaultListModel1.addElement("ipsum");
		defaultListModel1.addElement("aucupatum");
		defaultListModel1.addElement("versatio");
		venvListComponent.setModel(defaultListModel1);
		venvListComponent.setToolTipText("");
		scrollPane1.setViewportView(venvListComponent);
		final JScrollPane scrollPane2 = new JScrollPane();
		scrollPane2.setToolTipText("");
		panel3.add(
			scrollPane2,
			new GridConstraints(
				1,
				0,
				2,
				1,
				GridConstraints.ANCHOR_WEST,
				GridConstraints.FILL_VERTICAL,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		scrollPane2.setBorder(
			BorderFactory.createTitledBorder(
				null,
				"",
				TitledBorder.DEFAULT_JUSTIFICATION,
				TitledBorder.DEFAULT_POSITION,
				null,
				null
			)
		);
		packagesTable = new JTable();
		packagesTable.setToolTipText(
			"Packages installed in the current virtualenv"
		);
		scrollPane2.setViewportView(packagesTable);
		final JPanel panel4 = new JPanel();
		panel4.setLayout(
			new GridLayoutManager(1, 1, new Insets(0, 0, 0, 0), -1, -1)
		);
		panel1.add(
			panel4,
			new GridConstraints(
				0,
				2,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		browsePanel = new JPanel();
		browsePanel.setLayout(
			new GridLayoutManager(11, 3, new Insets(3, 3, 3, 3), 0, -1)
		);
		panel4.add(
			browsePanel,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_NORTH,
				GridConstraints.FILL_HORIZONTAL,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				null,
				new Dimension(300, -1),
				0,
				false
			)
		);
		frameworkConfigPanel = new JPanel();
		frameworkConfigPanel.setLayout(
			new GridLayoutManager(2, 3, new Insets(0, 0, 10, 10), -1, -1)
		);
		frameworkConfigPanel.setEnabled(false);
		frameworkConfigPanel.setVisible(false);
		browsePanel.add(
			frameworkConfigPanel,
			new GridConstraints(
				1,
				0,
				1,
				3,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		frameworkBrowseButton = new JButton();
		frameworkBrowseButton.setText("Browse");
		frameworkConfigPanel.add(
			frameworkBrowseButton,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				1,
				false
			)
		);
		final Spacer spacer1 = new Spacer();
		frameworkConfigPanel.add(
			spacer1,
			new GridConstraints(
				1,
				2,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_HORIZONTAL,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				1,
				null,
				null,
				null,
				0,
				false
			)
		);
		frameworkPathTextArea = new JTextArea();
		frameworkPathTextArea.setText("framework path");
		frameworkConfigPanel.add(
			frameworkPathTextArea,
			new GridConstraints(
				0,
				1,
				1,
				1,
				GridConstraints.ANCHOR_SOUTH,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				new Dimension(150, 10),
				null,
				0,
				false
			)
		);
		frameworkPathField = new JTextField();
		frameworkPathField.setHorizontalAlignment(4);
		frameworkPathField.setText("");
		frameworkConfigPanel.add(
			frameworkPathField,
			new GridConstraints(
				1,
				1,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				new Dimension(50, 10),
				null,
				0,
				false
			)
		);
		scriptConfigPanel = new JPanel();
		scriptConfigPanel.setLayout(
			new GridLayoutManager(2, 1, new Insets(0, 0, 10, 10), -1, -1)
		);
		scriptConfigPanel.setToolTipText("");
		browsePanel.add(
			scriptConfigPanel,
			new GridConstraints(
				5,
				0,
				1,
				3,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		scriptBrowseButton = new JButton();
		scriptBrowseButton.setText("Browse");
		scriptConfigPanel.add(
			scriptBrowseButton,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				1,
				false
			)
		);
		scriptPathTextArea = new JLabel();
		scriptPathTextArea.setText("Add an existing python script");
		scriptConfigPanel.add(
			scriptPathTextArea,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_SOUTH,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				new Dimension(-1, 10),
				null,
				0,
				false
			)
		);
		final JPanel panel5 = new JPanel();
		panel5.setLayout(
			new GridLayoutManager(2, 1, new Insets(0, 0, 10, 10), -1, -1)
		);
		browsePanel.add(
			panel5,
			new GridConstraints(
				7,
				0,
				1,
				3,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		createButton = new JButton();
		createButton.setText("Create new script");
		panel5.add(
			createButton,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				1,
				false
			)
		);
		final Spacer spacer2 = new Spacer();
		panel5.add(
			spacer2,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_VERTICAL,
				1,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				new Dimension(-1, 10),
				null,
				0,
				false
			)
		);
		final JPanel panel6 = new JPanel();
		panel6.setLayout(
			new GridLayoutManager(2, 1, new Insets(0, 0, 10, 10), -1, -1)
		);
		panel6.setToolTipText("");
		browsePanel.add(
			panel6,
			new GridConstraints(
				6,
				0,
				1,
				3,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		openScriptButton = new JButton();
		openScriptButton.setText("Open selected script");
		openScriptButton.setToolTipText(
			"Open the script with the command defined in \"Settings\""
		);
		panel6.add(
			openScriptButton,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				1,
				false
			)
		);
		final Spacer spacer3 = new Spacer();
		panel6.add(
			spacer3,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_VERTICAL,
				1,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				new Dimension(-1, 10),
				null,
				0,
				false
			)
		);
		listPannel = new JPanel();
		listPannel.setLayout(
			new GridLayoutManager(3, 1, new Insets(0, 0, 0, 0), -1, -1)
		);
		listPannel.setToolTipText("");
		browsePanel.add(
			listPannel,
			new GridConstraints(
				10,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		listPannel.setBorder(
			BorderFactory.createTitledBorder(
				null,
				"",
				TitledBorder.DEFAULT_JUSTIFICATION,
				TitledBorder.DEFAULT_POSITION,
				null,
				null
			)
		);
		final JScrollPane scrollPane3 = new JScrollPane();
		listPannel.add(
			scrollPane3,
			new GridConstraints(
				2,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				1,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		venvScriptList = new JList();
		venvScriptList.setMaximumSize(new Dimension(65, 150));
		final DefaultListModel defaultListModel2 = new DefaultListModel();
		defaultListModel2.addElement("default.py");
		defaultListModel2.addElement("crypto.py");
		defaultListModel2.addElement("recon.py");
		venvScriptList.setModel(defaultListModel2);
		venvScriptList.setPreferredSize(new Dimension(65, 300));
		venvScriptList.setToolTipText("");
		venvScriptList.putClientProperty("List.isFileList", Boolean.TRUE);
		scrollPane3.setViewportView(venvScriptList);
		final JLabel label1 = new JLabel();
		label1.setHorizontalAlignment(0);
		label1.setHorizontalTextPosition(0);
		label1.setText("Selected script: ");
		listPannel.add(
			label1,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_FIXED,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				0,
				false
			)
		);
		selectedScriptLabel = new JLabel();
		selectedScriptLabel.setText("");
		listPannel.add(
			selectedScriptLabel,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_FIXED,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				0,
				false
			)
		);
		final JPanel panel7 = new JPanel();
		panel7.setLayout(
			new GridLayoutManager(2, 1, new Insets(0, 0, 10, 10), -1, -1)
		);
		panel7.setToolTipText("");
		browsePanel.add(
			panel7,
			new GridConstraints(
				8,
				0,
				1,
				3,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		panel7.setBorder(
			BorderFactory.createTitledBorder(
				null,
				"",
				TitledBorder.DEFAULT_JUSTIFICATION,
				TitledBorder.DEFAULT_POSITION,
				null,
				null
			)
		);
		openFolderButton = new JButton();
		openFolderButton.setText("Open script folder");
		openFolderButton.setToolTipText(
			"Open the containing folder using the command defined in \"Settings\""
		);
		panel7.add(
			openFolderButton,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				1,
				false
			)
		);
		final Spacer spacer4 = new Spacer();
		panel7.add(
			spacer4,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_VERTICAL,
				1,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				new Dimension(-1, 10),
				null,
				0,
				false
			)
		);
		scalpelIsENABLEDButton = new JButton();
		scalpelIsENABLEDButton.setForeground(new Color(-4473925));
		scalpelIsENABLEDButton.setHideActionText(false);
		scalpelIsENABLEDButton.setText("Scalpel is ENABLED");
		scalpelIsENABLEDButton.setToolTipText(
			"Button to enable or disable Scalpel hooks"
		);
		browsePanel.add(
			scalpelIsENABLEDButton,
			new GridConstraints(
				3,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_HORIZONTAL,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				0,
				false
			)
		);
		final Spacer spacer5 = new Spacer();
		browsePanel.add(
			spacer5,
			new GridConstraints(
				4,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_VERTICAL,
				1,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				new Dimension(-1, 15),
				null,
				null,
				0,
				false
			)
		);
		final Spacer spacer6 = new Spacer();
		browsePanel.add(
			spacer6,
			new GridConstraints(
				2,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_VERTICAL,
				1,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				new Dimension(-1, 5),
				null,
				null,
				0,
				false
			)
		);
		final JPanel panel8 = new JPanel();
		panel8.setLayout(
			new GridLayoutManager(2, 1, new Insets(0, 0, 10, 10), -1, -1)
		);
		panel8.setToolTipText("");
		browsePanel.add(
			panel8,
			new GridConstraints(
				9,
				0,
				1,
				3,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		panel8.setBorder(
			BorderFactory.createTitledBorder(
				null,
				"",
				TitledBorder.DEFAULT_JUSTIFICATION,
				TitledBorder.DEFAULT_POSITION,
				null,
				null
			)
		);
		resetTerminalButton = new JButton();
		resetTerminalButton.setText("Reset terminal");
		resetTerminalButton.setToolTipText(
			"Reset the terminal in case it gets broken"
		);
		panel8.add(
			resetTerminalButton,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				1,
				false
			)
		);
		final Spacer spacer7 = new Spacer();
		panel8.add(
			spacer7,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_VERTICAL,
				1,
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				new Dimension(-1, 10),
				null,
				0,
				false
			)
		);
		outputTabPanel = new JPanel();
		outputTabPanel.setLayout(
			new GridLayoutManager(2, 2, new Insets(0, 0, 0, 0), -1, -1)
		);
		tabbedPane1.addTab("Script output", outputTabPanel);
		final JPanel panel9 = new JPanel();
		panel9.setLayout(
			new GridLayoutManager(2, 1, new Insets(0, 0, 0, 0), -1, -1)
		);
		outputTabPanel.add(
			panel9,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_FIXED,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		stdoutScrollPane = new JScrollPane();
		panel9.add(
			stdoutScrollPane,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		stdoutTextArea = new JTextArea();
		stdoutTextArea.setEditable(false);
		stdoutTextArea.setLineWrap(true);
		stdoutTextArea.setText("");
		stdoutTextArea.setWrapStyleWord(true);
		stdoutTextArea.putClientProperty("html.disable", Boolean.TRUE);
		stdoutScrollPane.setViewportView(stdoutTextArea);
		final JLabel label2 = new JLabel();
		label2.setText("Output");
		panel9.add(
			label2,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_FIXED,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				0,
				false
			)
		);
		final JPanel panel10 = new JPanel();
		panel10.setLayout(
			new GridLayoutManager(2, 1, new Insets(0, 0, 0, 0), -1, -1)
		);
		outputTabPanel.add(
			panel10,
			new GridConstraints(
				0,
				1,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		stderrScrollPane = new JScrollPane();
		panel10.add(
			stderrScrollPane,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		stderrTextArea = new JTextArea();
		stderrTextArea.setEditable(false);
		stderrTextArea.setLineWrap(true);
		stderrTextArea.setText("");
		stderrTextArea.putClientProperty("html.disable", Boolean.TRUE);
		stderrScrollPane.setViewportView(stderrTextArea);
		final JLabel label3 = new JLabel();
		label3.setText("Error");
		panel10.add(
			label3,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_NONE,
				GridConstraints.SIZEPOLICY_FIXED,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				0,
				false
			)
		);
		settingsTab = new JPanel();
		settingsTab.setLayout(new BorderLayout(0, 0));
		settingsTab.putClientProperty("html.disable", Boolean.TRUE);
		tabbedPane1.addTab("Settings", settingsTab);
		final JPanel panel11 = new JPanel();
		panel11.setLayout(
			new FormLayout(
				"fill:d:grow",
				"center:d:noGrow,top:4dlu:noGrow,center:max(d;4px):noGrow"
			)
		);
		tabbedPane1.addTab("Help", panel11);
		helpTextPane = new JTextPane();
		helpTextPane.setContentType("text/html");
		helpTextPane.setEditable(false);
		helpTextPane.setEnabled(true);
		helpTextPane.setText(
			"<html>\n  <head>\n    \n  </head>\n  <body>\n    <p>\n      To access the documentation: <a href=\"https://ambionics.github.io/scalpel/public/\">Click \n      here</a>\n    </p>\n    <p>\n      To access the FAQ and common issues: <a href=\"https://ambionics.github.io/scalpel/public/faq\">Click \n      Here </a>\n    </p>\n    <p>\n      To fully uninstall Scalpel, remove the ~/.scalpel/ folder in your home \n      directory and make sure to remove the extension from Burp\n    </p>\n    <p>\n      To reinstall Scalpel simply restart Burp and reload the extension\n    </p>\n    <p>\n      If you have previously installed Scalpel and left the installation in a \n      broken state, you must fully uninstall Scalpel before reinstalling it\n    </p>\n    <p>\n      If Scalpel fails to load properly, make you sure you have installed all \n      the dependencies specified in the <a href=\"https://github.com/ambionics/scalpel/blob/main/README.md\">Github \n      README</a>, and that your Python version is supported\n    </p>\n    <p>\n      If you fail to troubleshoot a failed install, please open an issue on \n      the <a href=\"https://github.com/ambionics/scalpel\">GitHub page</a> and \n      include the content of the &quot;Debug Info&quot; tab\n    </p>\n    <p>\n      Note: To reload Scalpel, you MUST restart Burp entirely\n    </p>\n  </body>\n</html>\n"
		);
		CellConstraints cc = new CellConstraints();
		panel11.add(helpTextPane, cc.xy(1, 1));
		openIssueOnGitHubButton = new JButton();
		openIssueOnGitHubButton.setText("Open an issue on GitHub");
		panel11.add(
			openIssueOnGitHubButton,
			new CellConstraints(
				1,
				3,
				1,
				1,
				CellConstraints.LEFT,
				CellConstraints.DEFAULT,
				new Insets(0, 5, 0, 0)
			)
		);
		final JPanel panel12 = new JPanel();
		panel12.setLayout(
			new GridLayoutManager(2, 1, new Insets(0, 0, 0, 0), -1, -1)
		);
		tabbedPane1.addTab("Debug Info", panel12);
		final JScrollPane scrollPane4 = new JScrollPane();
		scrollPane4.setHorizontalScrollBarPolicy(30);
		panel12.add(
			scrollPane4,
			new GridConstraints(
				0,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_BOTH,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_WANT_GROW,
				null,
				null,
				null,
				0,
				false
			)
		);
		debugInfoTextPane = new JTextPane();
		debugInfoTextPane.setEditable(false);
		debugInfoTextPane.setText("");
		debugInfoTextPane.setToolTipText(
			"Transmit this when asking for support."
		);
		debugInfoTextPane.putClientProperty("html.disable", Boolean.TRUE);
		scrollPane4.setViewportView(debugInfoTextPane);
		copyToClipboardButton = new JButton();
		copyToClipboardButton.setText("Copy to clipboard");
		panel12.add(
			copyToClipboardButton,
			new GridConstraints(
				1,
				0,
				1,
				1,
				GridConstraints.ANCHOR_CENTER,
				GridConstraints.FILL_HORIZONTAL,
				GridConstraints.SIZEPOLICY_CAN_SHRINK |
				GridConstraints.SIZEPOLICY_CAN_GROW,
				GridConstraints.SIZEPOLICY_FIXED,
				null,
				null,
				null,
				0,
				false
			)
		);
	}

	/**
	 * @noinspection ALL
	 */
	public JComponent $$$getRootComponent$$$() {
		return rootPanel;
	}
}
