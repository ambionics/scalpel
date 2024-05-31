package lexfo.scalpel.components;

import java.awt.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import javax.swing.*;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

public class SettingsPanel extends JPanel {

	private final GridBagConstraints gbc = new GridBagConstraints();
	private final Map<String, JComponent> settingsComponentsByKey = new HashMap<>();
	private final Map<String, String> keyToLabel = new HashMap<>();
	private final List<Consumer<Map<String, String>>> changeListeners = new ArrayList<>();

	public SettingsPanel() {
		setLayout(new GridBagLayout());
		gbc.gridwidth = GridBagConstraints.REMAINDER;
		gbc.anchor = GridBagConstraints.WEST;
		gbc.insets = new Insets(4, 4, 4, 4);
	}

	public void addListener(Consumer<Map<String, String>> listener) {
		changeListeners.add(listener);
	}

	public void addCheckboxSetting(
		String key,
		String label,
		boolean isSelected
	) {
		JCheckBox checkBox = new JCheckBox();
		checkBox.setSelected(isSelected);
		checkBox.addActionListener(e -> notifyChangeListeners());
		addSettingComponent(key, label, checkBox);
	}

	public void addTextFieldSetting(String key, String label, String text) {
		JTextField textField = new JTextField(text, 20);

		// Debounce timer
		Timer timer = new Timer(300, e -> notifyChangeListeners()); // 300 ms delay
		timer.setRepeats(false); // Ensure the timer only runs once per event

		textField
			.getDocument()
			.addDocumentListener(
				new DocumentListener() {
					public void insertUpdate(DocumentEvent e) {
						timer.restart();
					}

					public void removeUpdate(DocumentEvent e) {
						timer.restart();
					}

					public void changedUpdate(DocumentEvent e) {
						timer.restart();
					}
				}
			);

		addSettingComponent(key, label, textField);
	}

	public void addDropdownSetting(
		String key,
		String label,
		String[] options,
		String selectedItem
	) {
		JComboBox<String> comboBox = new JComboBox<>(options);
		comboBox.setSelectedItem(selectedItem);
		comboBox.addActionListener(e -> notifyChangeListeners());
		addSettingComponent(key, label, comboBox);
	}

	private void addSettingComponent(
		String key,
		String label,
		JComponent component
	) {
		settingsComponentsByKey.put(key, component);
		keyToLabel.put(key, label);
		JPanel panel = new JPanel(new FlowLayout(FlowLayout.LEFT));
		panel.add(new JLabel(label));
		panel.add(component);
		add(panel, gbc);
	}

	public void addInformationText(String text) {
		JLabel infoLabel = new JLabel(text);
		JPanel panel = new JPanel(new FlowLayout(FlowLayout.LEFT));
		panel.add(infoLabel);
		add(panel, gbc);
	}

	private void notifyChangeListeners() {
		Map<String, String> settingsValues = getSettingsValues();
		for (Consumer<Map<String, String>> listener : changeListeners) {
			listener.accept(settingsValues);
		}
	}

	public Map<String, String> getSettingsValues() {
		Map<String, String> settingsValues = new HashMap<>();
		settingsComponentsByKey.forEach((key, component) -> {
			String value = "";
			if (component instanceof JCheckBox) {
				value = ((JCheckBox) component).isSelected() ? "True" : "False";
			} else if (component instanceof JTextField) {
				value = ((JTextField) component).getText();
			} else if (component instanceof JComboBox) {
				value = (String) ((JComboBox<?>) component).getSelectedItem();
			}
			settingsValues.put(key, value);
		});
		return settingsValues;
	}

	public void setSettingsValues(Map<String, String> settingsValues) {
		settingsValues.forEach((key, value) -> {
			JComponent component = settingsComponentsByKey.get(key);
			if (component instanceof JCheckBox) {
				((JCheckBox) component).setSelected(
						Boolean.parseBoolean(value)
					);
			} else if (component instanceof JTextField) {
				((JTextField) component).setText(value);
			} else if (component instanceof JComboBox) {
				((JComboBox) component).setSelectedItem(value);
			}
		});
		notifyChangeListeners();
	}
}
