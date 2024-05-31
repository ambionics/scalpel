package lexfo.scalpel.components;

import java.awt.*;
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;
import javax.swing.*;

public class PlaceholderTextField extends JTextField {

	private String placeholder;

	public PlaceholderTextField(String placeholder) {
		this.placeholder = placeholder;
		addFocusListener(
			new FocusAdapter() {
				@Override
				public void focusGained(FocusEvent e) {
					if (getText().isEmpty()) {
						setText("");
						repaint();
					}
				}

				@Override
				public void focusLost(FocusEvent e) {
					if (getText().isEmpty()) {
						setText("");
						repaint();
					}
				}
			}
		);
	}

	@Override
	protected void paintComponent(Graphics g) {
		super.paintComponent(g);

		if (getText().isEmpty() && !hasFocus()) {
			Graphics2D g2 = (Graphics2D) g.create();
			g2.setColor(Color.GRAY);
			g2.setFont(getFont().deriveFont(Font.ITALIC));
			int padding = (getHeight() - getFont().getSize()) / 2;
			g2.drawString(
				placeholder,
				getInsets().left,
				getHeight() - padding - 1
			);
			g2.dispose();
		}
	}

	public static void main(String[] args) {
		JFrame frame = new JFrame("Placeholder JTextField Example");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setLayout(new FlowLayout());

		PlaceholderTextField textField = new PlaceholderTextField(
			"Enter text here..."
		);
		textField.setColumns(20);

		frame.add(textField);
		frame.pack();
		frame.setLocationRelativeTo(null);
		frame.setVisible(true);
	}
}
