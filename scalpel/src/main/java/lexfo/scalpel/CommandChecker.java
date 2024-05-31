package lexfo.scalpel;

import java.io.File;

/**
 * Provides utilities to get default commands.
 */
public class CommandChecker {

	public static String getAvailableCommand(String... commands) {
		for (int i = 0; i < commands.length - 1; i++) {
			try {
				final String cmd = commands[i];
				if (cmd == null) {
					continue;
				}

				final String binary = extractBinary(cmd);
				if (isCommandAvailable(binary)) {
					return cmd;
				}
			} catch (Throwable e) {
				ScalpelLogger.logStackTrace(e);
			}
		}
		// If no command matched, return the last one
		return commands[commands.length - 1];
	}

	private static String extractBinary(String command) {
		final int spaceIndex = command.indexOf(' ');
		if (spaceIndex != -1) {
			return command.substring(0, spaceIndex);
		}
		return command;
	}

	private static boolean isCommandAvailable(String command) {
		// Check if the command is an absolute path
		final File commandFile = new File(command);
		if (commandFile.isAbsolute()) {
			return commandFile.exists() && commandFile.canExecute();
		}

		// Check in each directory listed in PATH
		final String path = System.getenv("PATH");
		if (path != null) {
			for (final String dir : path.split(File.pathSeparator)) {
				final File file = new File(dir, command);
				if (file.exists() && file.canExecute()) {
					return true;
				}
			}
		}
		return false;
	}
}
