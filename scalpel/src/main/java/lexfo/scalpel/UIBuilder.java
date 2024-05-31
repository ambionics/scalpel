package lexfo.scalpel;

import burp.api.montoya.MontoyaApi;
import burp.api.montoya.ui.Theme;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import javax.swing.*;
import org.apache.commons.io.FileUtils;

/**
	Provides methods for constructing the Burp Suite UI.
*/
public class UIBuilder {

	/**
		Constructs the configuration Burp tab.

		@param executor The ScalpelExecutor object to use.
		@param defaultScriptPath The default text content
		@return The constructed tab.
	 */
	public static final Component constructConfigTab(
		MontoyaApi API,
		ScalpelExecutor executor,
		Config config,
		Theme theme
	) {
		return new ConfigTab(API, executor, config, theme).uiComponent();
	}

	/**
		Constructs the debug Python testing Burp tab.
		@param executor The ScalpelExecutor object to use.
		@param logger The Logging object to use.
		@return The constructed tab.
	*/
	public static final Component constructScalpelInterpreterTab(
		Config config,
		ScalpelExecutor executor
	) {
		// Split pane
		JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
		JSplitPane scriptingPane = new JSplitPane(JSplitPane.VERTICAL_SPLIT);
		JTextArea outputArea = new JTextArea();
		JEditorPane editorPane = new JEditorPane();
		JButton button = new JButton("Run script.");

		button.addActionListener((ActionEvent e) -> {
			ScalpelLogger.trace("Clicked button");
			final String scriptContent = editorPane.getText();
			try {
				final String[] scriptOutput = executor.evalAndCaptureOutput(
					scriptContent
				);

				final String txt = String.format(
					"stdout:\n------------------\n%s\n------------------\n\nstderr:\n------------------\n%s",
					scriptOutput[0],
					scriptOutput[1]
				);

				outputArea.setText(txt);
			} catch (Throwable exception) {
				outputArea.setText(exception.getMessage());
				outputArea.append("\n\n");

				final String stackTrace = Arrays
					.stream(exception.getStackTrace())
					.map(StackTraceElement::toString)
					.reduce((a, b) -> a + "\n" + b)
					.orElse("No stack trace.");

				outputArea.append(stackTrace);
			}
			ScalpelLogger.trace("Handled action.");
		});

		final File file = config.getFrameworkPath().toFile();
		editorPane.setText(
			IO.ioWrap(
				() -> FileUtils.readFileToString(file, StandardCharsets.UTF_8),
				() -> ""
			)
		);

		outputArea.setEditable(false);
		scriptingPane.setLeftComponent(new JScrollPane(editorPane));
		scriptingPane.setRightComponent(new JScrollPane(outputArea));
		scriptingPane.setResizeWeight(0.5);

		splitPane.setResizeWeight(1);
		splitPane.setLeftComponent(scriptingPane);
		splitPane.setRightComponent(button);

		return splitPane;
	}
}
