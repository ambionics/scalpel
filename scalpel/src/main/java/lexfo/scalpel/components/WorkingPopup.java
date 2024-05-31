package lexfo.scalpel.components;

import java.awt.*;
import java.util.function.Consumer;
import javax.swing.*;

/**
	Provides a blocking wait dialog GUI popup.
*/
public class WorkingPopup {

	/**
		Shows a blocking wait dialog.

		@param task The task to run while the dialog is shown.
	*/
	public static void showBlockingWaitDialog(
		String message,
		Consumer<JLabel> task
	) {
		final JFrame parent = new JFrame();
		parent.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);

		final JDialog dialog = new JDialog(parent, "Please wait...", true);
		dialog.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);

		final JLabel label = new JLabel(message);
		label.setHorizontalAlignment(SwingConstants.CENTER);
		label.setBorder(BorderFactory.createEmptyBorder(20, 0, 20, 0));
		dialog.add(label, BorderLayout.CENTER);

		dialog.setLocationRelativeTo(parent);

		final Thread taskThread = new Thread(() -> {
			try {
				task.accept(label);
			} finally {
				SwingUtilities.invokeLater(dialog::dispose);
			}
		});
		taskThread.start();

		SwingUtilities.invokeLater(() -> {
			dialog.pack();
			dialog.setVisible(true);
		});
	}
}
