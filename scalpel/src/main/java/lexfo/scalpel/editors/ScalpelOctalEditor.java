package lexfo.scalpel.editors;

import burp.api.montoya.MontoyaApi;
import burp.api.montoya.ui.editor.extension.EditorCreationContext;
import lexfo.scalpel.EditorType;
import lexfo.scalpel.ScalpelEditorTabbedPane;
import lexfo.scalpel.ScalpelExecutor;
import org.exbin.bined.CodeType;

public class ScalpelOctalEditor extends ScalpelGenericBinaryEditor {

	public ScalpelOctalEditor(
		String name,
		Boolean editable,
		MontoyaApi API,
		EditorCreationContext creationContext,
		EditorType type,
		ScalpelEditorTabbedPane provider,
		ScalpelExecutor executor
	) {
		super(
			name,
			editable,
			API,
			creationContext,
			type,
			provider,
			executor,
			CodeType.OCTAL
		);
		// this.editor.setMaxBytesPerRow(10);
	}
}
