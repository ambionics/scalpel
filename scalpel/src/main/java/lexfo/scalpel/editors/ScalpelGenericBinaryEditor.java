package lexfo.scalpel.editors;

import burp.api.montoya.MontoyaApi;
import burp.api.montoya.core.ByteArray;
import burp.api.montoya.ui.Selection;
import burp.api.montoya.ui.editor.extension.EditorCreationContext;
import burp.api.montoya.ui.editor.extension.EditorMode;
import java.awt.*;
import java.io.IOException;
import java.util.Optional;
import lexfo.scalpel.EditorType;
import lexfo.scalpel.ScalpelEditorTabbedPane;
import lexfo.scalpel.ScalpelExecutor;
import lexfo.scalpel.ScalpelLogger;
import org.exbin.auxiliary.paged_data.BinaryData;
import org.exbin.auxiliary.paged_data.ByteArrayEditableData;
import org.exbin.bined.CodeType;
import org.exbin.bined.EditMode;
import org.exbin.bined.SelectionRange;
import org.exbin.bined.swing.basic.CodeArea;

// https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/ui/editor/extension/ExtensionProvidedHttpRequestEditor.html
// https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/ui/editor/extension/ExtensionProvidedHttpResponseEditor.html
/**
  Hexadecimal editor implementation for a Scalpel editor
  Users can press their keyboard's INSER key to enter insertion mode
  (which is impossible in Burp's native hex editor)
*/
public class ScalpelGenericBinaryEditor extends AbstractEditor {

	protected final CodeArea editor;

	private ByteArray oldContent = null;

	/**
		Constructs a new Scalpel editor.
		
		@param API The Montoya API object.
		@param creationContext The EditorCreationContext object containing information about the editor.
		@param type The editor type (REQUEST or RESPONSE).
		@param provider The ScalpelProvidedEditor object that instantiated this editor.
		@param executor The executor to use.
	*/
	public ScalpelGenericBinaryEditor(
		String name,
		Boolean editable,
		MontoyaApi API,
		EditorCreationContext creationContext,
		EditorType type,
		ScalpelEditorTabbedPane provider,
		ScalpelExecutor executor,
		CodeType mode
	) {
		super(name, editable, API, creationContext, type, provider, executor);
		try {
			// Create the base BinEd editor component.
			this.editor = new CodeArea();
			this.editor.setCodeType(mode);
			this.editor.setFont(API.userInterface().currentEditorFont());

			// Charset to display whitespaces as something else.
			// editor.setCharset(new DisplayableWhiteSpaceCharset());

			// Decide wherever the editor must be editable or read only depending on context.
			final boolean isEditable =
				editable &&
				creationContext.editorMode() != EditorMode.READ_ONLY;

			// EXPANDING means that editing the content and modifying the content in a way that increases it's total size are allowed.
			// (as opposed to INPLACE or CAPPED where exceeding data is removed)
			final EditMode editMode = isEditable
				? EditMode.EXPANDING
				: EditMode.READ_ONLY;

			editor.setEditMode(editMode);
		} catch (Throwable e) {
			// Log the error.
			ScalpelLogger.error("Couldn't instantiate new editor:");

			// Log the stack trace.
			ScalpelLogger.logStackTrace(e);

			// Throw the error again.
			throw e;
		}
	}

	/**
	 * Convert from Burp format to BinEd format
	 * @param binaryData Bytes as Burp format
	 * @return Bytes as BinEd format
	 */
	private BinaryData byteArrayToBinaryData(ByteArray byteArray) {
		return new ByteArrayEditableData(byteArray.getBytes());
	}

	/**
	 * Convert from BinEd format to Burp format
	 * @param binaryData Bytes as BinEd format
	 * @return Bytes as Burp format
	 */
	private ByteArray binaryDataToByteArray(BinaryData binaryData) {
		// Load the data
		final ByteArrayEditableData buffer = new ByteArrayEditableData();
		try {
			buffer.loadFromStream(binaryData.getDataInputStream());
		} catch (IOException ex) {
			throw new RuntimeException(
				"Unexpected error happened while loading bytes from hex editor"
			);
		}

		final byte[] bytes = buffer.getData();

		// Convert bytes to Burp ByteArray
		return ByteArray.byteArray(bytes);
	}

	protected void setEditorContent(ByteArray bytes) {
		// Convert from burp format to BinEd format
		final BinaryData newContent = byteArrayToBinaryData(bytes);
		editor.setContentData(newContent);

		// Keep the old content for isModified()
		oldContent = bytes;
	}

	protected ByteArray getEditorContent() {
		try {
			// Convert BinEd format to Burp format
			return binaryDataToByteArray(editor.getContentData());
		} catch (RuntimeException ex) {
			// We have to catch and handle this here because otherwise Burp explodes
			ScalpelLogger.error("Couldn't convert bytes:");
			ScalpelLogger.logStackTrace(ex);

			return oldContent;
		}
	}

	/**
		Returns the underlying UI component.
		(called by Burp)

		@return The underlying UI component.
	*/
	@Override
	public Component getUiComponent() {
		return editor;
	}

	/**
		Returns the selected data.
		(called by Burp)

		@return The selected data.
	*/
	@Override
	public Selection selectedData() {
		final SelectionRange selected = editor.getSelection();

		// Convert BinEd selection range to Burp selection range
		return Selection.selection(
			(int) selected.getStart(),
			(int) selected.getEnd()
		);
	}

	/**
		Returns whether the editor has been modified.
		(called by Burp)

		@return Whether the editor has been modified.
	*/
	@Override
	public boolean isModified() {
		// Check if current content is the same as the provided data.
		return Optional
			.ofNullable(this.getEditorContent())
			.map(c -> !c.equals(oldContent))
			.orElse(false);
	}
}
