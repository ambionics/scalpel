package lexfo.scalpel.components;

import java.awt.*;
import java.util.regex.*;
import javax.swing.*;
import javax.swing.event.HyperlinkEvent;

public class ErrorDialog {

	public static void showErrorDialog(Frame parent, String errorText) {
		// Create a JEditorPane for clickable links and selectable text
		final JEditorPane messagePane = new JEditorPane("text/html", "");
		messagePane.setEditable(false);
		messagePane.setBackground(null);
		messagePane.setOpaque(false);
		messagePane.setContentType("text/html");

		// Sanitize and format the error message
		final String sanitizedHTML = sanitizeHTML(errorText);
		final String formattedMessage = linkifyURLs(sanitizedHTML);

		// Set HTML content to make links clickable and text selectable
		final String message =
			"<html><body style='font-family: sans-serif;'>" +
			formattedMessage.replace("\n", "<br>") +
			"</body></html>";
		messagePane.setText(message);

		// Make links open in user's default browser
		messagePane.addHyperlinkListener(hyperlinkEvent -> {
			if (
				HyperlinkEvent.EventType.ACTIVATED.equals(
					hyperlinkEvent.getEventType()
				)
			) {
				try {
					Desktop
						.getDesktop()
						.browse(hyperlinkEvent.getURL().toURI());
				} catch (Throwable ex) {
					ex.printStackTrace();
				}
			}
		});

		// Wrap in a scroll pane
		final JScrollPane scrollPane = new JScrollPane(messagePane);
		scrollPane.setBorder(null);
		scrollPane.setPreferredSize(new Dimension(350, 150));

		// Show in JOptionPane
		JOptionPane.showMessageDialog(
			parent,
			scrollPane,
			"Installation Error",
			JOptionPane.ERROR_MESSAGE
		);
	}

	private static String sanitizeHTML(String text) {
		return text
			.replace("&", "&amp;")
			.replace("<", "&lt;")
			.replace(">", "&gt;")
			.replace("\"", "&quot;")
			.replace("'", "&#x27;");
	}

	private static String linkifyURLs(String text) {
		// Regex to identify URLs
		Pattern pattern = Pattern.compile(
			"(https?://[\\w_\\-./?=&#]+)",
			Pattern.CASE_INSENSITIVE
		);
		Matcher matcher = pattern.matcher(text);
		StringBuffer sb = new StringBuffer();
		while (matcher.find()) {
			// Replace URLs with HTML links
			matcher.appendReplacement(sb, "<a href='$1'>$1</a>");
		}
		matcher.appendTail(sb);
		return sb.toString();
	}
}
