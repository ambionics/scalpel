package lexfo.scalpel;

import com.jediterm.terminal.emulator.ColorPalette;
import java.awt.*;

/**
 * Color palette for the embedded terminal
 * Contains colors for both light and dark theme
 */
public class Palette extends ColorPalette {

	private static final Color[] DARK_COLORS = new Color[] {
		new Color(0x2c2c2c), // Slightly lighter dark blue
		new Color(0xe60000), // Slightly lighter red
		new Color(0x00e600), // Slightly lighter green
		new Color(0xe6e600), // Slightly lighter yellow
		new Color(0x2e9afe), // Slightly lighter blue
		new Color(0xe600e6), // Slightly lighter magenta
		new Color(0x00e6e6), // Slightly lighter cyan
		new Color(0xf2f2f2), // Slightly lighter white
	
		// Bright versions of the ISO colors
		new Color(0x5f5f5f), // Bright black
		new Color(0xff5f5f), // Bright red
		new Color(0x5fff5f), // Bright green
		new Color(0xffff5f), // Bright yellow
		new Color(0x7da7ff), // Bright blue
		new Color(0xff5fff), // Bright magenta
		new Color(0x5fffff), // Bright cyan
		new Color(0xffffff), // Bright white
	};

	public static final ColorPalette DARK_PALETTE = new Palette(DARK_COLORS);

	private static final Color[] LIGHT_COLORS = new Color[] {
		new Color(0x1c1c1c), // Dark blue
		new Color(0xcd0000), // Red
		new Color(0x00cd00), // Green
		new Color(0xcdcd00), // Yellow
		new Color(0x1e90ff), // Blue
		new Color(0xcd00cd), // Magenta
		new Color(0x00cdcd), // Cyan
		new Color(0xd4d4d4), // Grayish white
	
		// Bright versions of the ISO colors
		new Color(0x555555), // Bright black
		new Color(0xff0000), // Bright red
		new Color(0x00ff00), // Bright green
		new Color(0xffff00), // Bright yellow
		new Color(0x6495ed), // Bright blue
		new Color(0xff00ff), // Bright magenta
		new Color(0x00ffff), // Bright cyan
		new Color(0xe5e5e5), // Bright grayish white
	};

	public static final ColorPalette LIGHT_PALETTE = new Palette(LIGHT_COLORS);

	private static final Color[] WINDOWS_COLORS = new Color[] {
		new Color(0x000000), //Black
		new Color(0x800000), //Red
		new Color(0x008000), //Green
		new Color(0x808000), //Yellow
		new Color(0x000080), //Blue
		new Color(0x800080), //Magenta
		new Color(0x008080), //Cyan
		new Color(0xc0c0c0), //White
		//Bright versions of the ISO colors
		new Color(0x808080), //Black
		new Color(0xff0000), //Red
		new Color(0x00ff00), //Green
		new Color(0xffff00), //Yellow
		new Color(0x4682b4), //Blue
		new Color(0xff00ff), //Magenta
		new Color(0x00ffff), //Cyan
		new Color(0xffffff), //White
	};

	public static final ColorPalette WINDOWS_PALETTE = new Palette(
		WINDOWS_COLORS
	);

	private final Color[] myColors;

	private Palette(Color[] colors) {
		myColors = colors;
	}

	@Override
	public Color getForegroundByColorIndex(int colorIndex) {
		return myColors[colorIndex];
	}

	@Override
	protected Color getBackgroundByColorIndex(int colorIndex) {
		return myColors[colorIndex];
	}
}
