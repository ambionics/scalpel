package lexfo.scalpel.components;

import burp.api.montoya.MontoyaApi;
import java.awt.*;
import java.util.Map;
import java.util.concurrent.ConcurrentLinkedQueue;
import javax.swing.*;
import lexfo.scalpel.ConfigTab;
import lexfo.scalpel.UIUtils;

public class ErrorPopup extends JFrame {

	private static final ConcurrentLinkedQueue<String> errorMessages = new ConcurrentLinkedQueue<>();
	private JTextArea errorArea;
	private JCheckBox suppressCheckBox;

	public ErrorPopup(MontoyaApi API) {
		super("Scalpel Error Log");
		setDefaultCloseOperation(WindowConstants.HIDE_ON_CLOSE);
		setSize((int) (400 * 1.8), (int) (300 * 1.5));
		setLocationRelativeTo(API.userInterface().swingUtils().suiteFrame());
		setLayout(new BorderLayout());

		errorArea = new JTextArea();
		errorArea.setEditable(false);

		final JScrollPane scrollPane = new JScrollPane(errorArea);
		UIUtils.setupAutoScroll(scrollPane, errorArea);

		add(scrollPane, BorderLayout.CENTER);

		suppressCheckBox =
			new JCheckBox("Do not display this again for this project");
		suppressCheckBox.addActionListener(e -> {
			boolean selected = suppressCheckBox.isSelected();
			ConfigTab
				.getInstance()
				.setSettings(
					Map.of(
						"displayProxyErrorPopup",
						!selected ? "True" : "False"
					)
				);
		});

		add(suppressCheckBox, BorderLayout.SOUTH);

		// Setup the window listener for handling the close operation
		addWindowListener(
			new java.awt.event.WindowAdapter() {
				@Override
				public void windowClosing(
					java.awt.event.WindowEvent windowEvent
				) {
					errorMessages.clear();
					errorArea.setText("");
					setVisible(false);
				}
			}
		);
	}

	public void displayErrors() {
		StringBuilder sb = new StringBuilder();
		for (String msg : errorMessages) {
			sb.append(msg).append("\n\n");
		}
		errorArea.setText(sb.toString());
		setVisible(true);
	}

	public void addError(String message) {
		errorMessages.add(message);
		displayErrors();
	}
}
