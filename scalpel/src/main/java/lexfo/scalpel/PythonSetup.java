package lexfo.scalpel;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * Utilities to initialize Java Embedded Python (jep)
 */
public class PythonSetup {

	public static void loadLibPython3() {
		final String libPath = executePythonCommand(
			"import sysconfig; print('/'.join([sysconfig.get_config_var('LIBDIR'), 'libpython' + sysconfig.get_config_var('VERSION') + '.dylib']))"
		);

		ScalpelLogger.all("Loading Python library from " + libPath);
		try {
			System.load(libPath);
		} catch (Throwable e) {
			throw new RuntimeException(
				"Failed loading" +
				libPath +
				"\nIf you are using an ARM/M1 macOS, make sure you installed the ARM/M1 Burp package and not the Intel one:\n" +
				"https://portswigger.net/burp/releases/professional-community-2023-10-1?requestededition=professional&requestedplatform=macos%20(arm/m1)",
				e
			);
		}
		ScalpelLogger.all("Successfully loaded Python library from " + libPath);
	}

	public static int getPythonVersion() {
		final String version = executePythonCommand(
			"import sys; print('.'.join(map(str, sys.version_info[:3])))"
		);

		if (version != null) {
			final String[] versionParts = version.split("\\.");
			final int major = Integer.parseInt(versionParts[0]);
			final int minor = Integer.parseInt(versionParts[1]);

			if (
				major < 3 ||
				(major == 3 && minor < Constants.MIN_SUPPORTED_PYTHON_VERSION)
			) {
				throw new RuntimeException(
					"Detected Python version " +
					version +
					". Requires Python version 3." +
					Constants.MIN_SUPPORTED_PYTHON_VERSION +
					" or greater."
				);
			}

			if (minor >= Constants.PREFERRED_PYTHON_VERSION) {
				return Constants.PREFERRED_PYTHON_VERSION;
			}
			return Constants.MIN_SUPPORTED_PYTHON_VERSION;
		} else {
			throw new RuntimeException("Failed to retrieve Python version.");
		}
	}

	public static String getUsedPythonBin() {
		// Get ~/.scalpel/venvs/default/.venv/bin/python if it exists, else, the Python in PATH
		// This is useful for cases where someone previously installed Scalpel with an older python version, and is now running Burp with a newer one.
		// The version that will actually be used will always be the default venv one.bu
		try {
			return Venv
				.getExecutablePath(
					Workspace.getVenvDir(Workspace.getDefaultWorkspace()),
					Constants.PYTHON_BIN
				)
				.toAbsolutePath()
				.toString();
		} catch (IOException e) {
			return Constants.PYTHON_BIN;
		}
	}

	public static String executePythonCommand(final String command) {
		try {
			final String[] cmd = { getUsedPythonBin(), "-c", command };

			final ProcessBuilder pb = new ProcessBuilder(cmd);
			pb.redirectErrorStream(true); // Redirect stderr to stdout

			final Process process = pb.start();
			final String output;
			try (
				BufferedReader reader = new BufferedReader(
					new InputStreamReader(process.getInputStream())
				)
			) {
				output = reader.readLine();
			}

			final int exitCode = process.waitFor();
			if (exitCode != 0) {
				throw new RuntimeException(
					"Python command failed with exit code " + exitCode
				);
			}

			return output;
		} catch (Throwable e) {
			throw new RuntimeException(e);
		}
	}
}
