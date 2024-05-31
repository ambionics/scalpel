package lexfo.scalpel;

import java.awt.Adjustable;
import java.util.concurrent.atomic.AtomicReference;
import javax.swing.JScrollBar;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.SwingUtilities;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

public class UIUtils {

	/**
	 * Set up auto-scrolling for a script output text area.
	 * <p>
	 * If the user scrolls up, auto-scroll is disabled.
	 * If the user scrolls to the bottom, auto-scroll is enabled.
	 *
	 * @param scrollPane The scroll pane containing the text area.
	 * @param textArea   The text area to auto-scroll.
	 */
	public static void setupAutoScroll(
		JScrollPane scrollPane,
		JTextArea textArea
	) {
		final JScrollBar verticalScrollBar = scrollPane.getVerticalScrollBar();

		// Unique auto-scroll flag for this text area
		final AtomicReference<Boolean> needAutoScroll = new AtomicReference<>(
			true
		); // Use an AtomicRef for mutable state inside lambdas

		verticalScrollBar.addAdjustmentListener(e -> {
			final Adjustable adjustable = e.getAdjustable();
			if (!e.getValueIsAdjusting()) {
				needAutoScroll.set(
					adjustable.getMaximum() -
					adjustable.getValue() -
					adjustable.getVisibleAmount() <
					50
				);
			}
		});

		textArea
			.getDocument()
			.addDocumentListener(
				new DocumentListener() {
					private void update() {
						if (needAutoScroll.get()) {
							// Scroll down
							SwingUtilities.invokeLater(() ->
								verticalScrollBar.setValue(
									verticalScrollBar.getMaximum()
								)
							);
						}
					}

					@Override
					public void insertUpdate(DocumentEvent e) {
						update();
					}

					@Override
					public void removeUpdate(DocumentEvent e) {
						update();
					}

					@Override
					public void changedUpdate(DocumentEvent e) {
						update();
					}
				}
			);
	}
}
