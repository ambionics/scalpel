package lexfo.scalpel;

import com.jediterm.terminal.Terminal;
import com.jediterm.terminal.ui.UIUtil;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Map;
import java.util.Optional;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import lexfo.scalpel.components.ErrorDialog;
import org.apache.commons.io.FileUtils;

/* 
 *  Note: The Scalpel data folder follows this architeture:
 * 
    ~
    └── .scalpel
        ├── extracted (ressources)
        ├── global.json
        ├── <project-data>.json
        └── venvs
            └── <workspace-name>
                ├── default.py
                └── .venv
*/

/**
 *  A workspace is a folder containing a venv and the associated scripts.
 * <br />
 *  We may still call that a "venv" in the front-end to avoid confusing the user.
 */
public class Workspace {

	public static final String VENV_DIR = ".venv";
	public static final String DEFAULT_VENV_NAME = "default";

	private static RuntimeException createExceptionFromProcess(
		Process proc,
		String msg,
		String defaultCmdLine
	) {
		final Stream<String> outStream = Stream.concat(
			proc.inputReader().lines(),
			proc.errorReader().lines()
		);
		final String out = outStream.collect(Collectors.joining("\n"));
		final String cmd = proc.info().commandLine().orElse(defaultCmdLine);

		return new RuntimeException(cmd + " failed:\n" + out + "\n" + msg);
	}

	/**
	 * Copy the script to the selected workspace
	 * @param scriptPath The script to copy
	 * @return The new file path
	 */
	public static Path copyScriptToWorkspace(
		final Path workspace,
		final Path scriptPath
	) {
		final File original = scriptPath.toFile();
		final String baseErrMsg =
			"Could not copy " + scriptPath + " to " + workspace + "\n";

		final Path destination = Optional
			.ofNullable(original)
			.filter(File::exists)
			.map(File::getName)
			.map(workspace::resolve)
			.orElseThrow(() ->
				new RuntimeException(baseErrMsg + "File not found")
			);

		if (Files.exists(destination)) {
			throw new RuntimeException(baseErrMsg + "File already exists");
		}

		try {
			return Files
				.copy(
					original.toPath(),
					destination,
					StandardCopyOption.REPLACE_EXISTING
				)
				.toAbsolutePath();
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}

	public static void copyWorkspaceFiles(Path workspace) throws IOException {
		final File source = RessourcesUnpacker.WORKSPACE_PATH.toFile();
		final File dest = workspace.toFile();
		FileUtils.copyDirectory(source, dest, true);
	}

	private static void println(Terminal terminal, String line) {
		terminal.writeUnwrappedString(line);
		terminal.carriageReturn();
		terminal.newLine();
	}

	public static void createAndInitWorkspace(
		Path workspace,
		Optional<Path> javaHome,
		Optional<Terminal> terminal
	) {
		// Run python -m venv <path>
		// Command to display in logs, actual command is formated in Venv.create
		final String cmd =
			Constants.PYTHON_BIN +
			" -m venv " +
			lexfo.scalpel.Terminal.escapeshellarg(
				getVenvDir(workspace).toString()
			);

		// Display the command in the terminal to avoid confusing the user
		terminal.ifPresent(t -> {
			t.reset();
			println(t, "$ " + cmd);
		});

		try {
			final Path venvDir = getVenvDir(workspace);
			final Process proc = Venv.create(venvDir);
			if (proc.exitValue() != 0) {
				throw createExceptionFromProcess(
					proc,
					"Ensure that pip3, python3.*-venv, python >= 3.8 and openjdk >= 17 are installed and in PATH.",
					cmd
				);
			}
			copyWorkspaceFiles(workspace);
		} catch (IOException | InterruptedException e) {
			throw new RuntimeException(e);
		}

		try {
			// Add default script.
			copyScriptToWorkspace(
				workspace,
				RessourcesUnpacker.DEFAULT_SCRIPT_PATH
			);
		} catch (RuntimeException e) {
			ScalpelLogger.error(
				"Default script could not be copied to " + workspace
			);
		}

		// Run pip install <dependencies>
		try {
			final Process proc;
			final Supplier<RuntimeException> toThrow = () ->
				new RuntimeException("JAVA_HOME was not provided.");

			if (javaHome.isPresent()) {
				proc =
					Venv.installDefaults(
						workspace,
						Map.of(
							"JAVA_HOME",
							javaHome.map(Path::toString).orElseThrow(toThrow)
						),
						true
					);
			} else {
				proc = Venv.installDefaults(workspace);
			}

			// Log pip output
			final BufferedReader stdout = proc.inputReader();
			while (proc.isAlive()) {
				Optional
					.ofNullable(stdout.readLine())
					.ifPresent(l -> {
						ScalpelLogger.all(l);

						// Display progess in embedded terminal
						terminal.ifPresent(t -> println(t, l));
					});
			}

			if (proc.exitValue() != 0) {
				final String linuxMsg =
					"On Debian/Ubuntu systems:\n\t" +
					"apt install build-essential python3-dev openjdk-17-jdk";

				final String winMsg =
					"On Windows:\n\t" +
					"Make sure you have installed Microsoft Visual C++ >=14.0 :\n\t" +
					"https://visualstudio.microsoft.com/visual-cpp-build-tools/";

				final String msg = UIUtil.isWindows ? winMsg : linuxMsg;

				throw createExceptionFromProcess(
					proc,
					"Could  not install dependencies\n" +
					"Make sure that a compiler, python dev libraries and openjdk 17 are properly installed and in PATH\n\n" +
					msg,
					"pip install jep ..."
				);
			}
		} catch (Throwable e) {
			// Display a popup explaining why the packages could not be installed
			ErrorDialog.showErrorDialog(
				null,
				"Could not install depencency packages.\n" +
				"Error: " +
				e.getMessage()
			);
			throw new RuntimeException(e);
		}
	}

	/**
	 * If a previous install failed because python dependencies were not installed,
	 * this will be false, in this case, we just try to resume the install.
	 */
	private static boolean isJepInstalled(Path workspace) throws IOException {
		final Path venvPath = workspace.resolve(VENV_DIR);
		final File dir = Venv.getSitePackagesPath(venvPath).toFile();

		final File[] jepDirs = dir.listFiles((__, name) -> name.matches("jep"));

		return jepDirs.length != 0;
	}

	/**
	 * Get the default workspace path.
	 * This is the workspace that will be used when the project is created.
	 * If the default workspace does not exist, it will be created.
	 * If the default workspace cannot be created, an exception will be thrown.
	 *
	 * @return The default workspace path.
	 */
	public static Path getOrCreateDefaultWorkspace(Path javaHome)
		throws IOException {
		final Path workspace = Path.of(
			Workspace.getWorkspacesDir().getPath(),
			DEFAULT_VENV_NAME
		);

		final File venvDir = workspace.resolve(VENV_DIR).toFile();

		// Return if default workspace dir already exists.
		if (!venvDir.exists()) {
			venvDir.mkdirs();
		} else if (!venvDir.isDirectory()) {
			throw new RuntimeException("Default venv path is not a directory");
		} else if (isJepInstalled(workspace)) {
			return workspace;
		}

		createAndInitWorkspace(
			workspace.toAbsolutePath(),
			Optional.of(javaHome),
			Optional.empty()
		);

		// Copy all example scripts to the default workspace.
		try (
			final DirectoryStream<Path> stream = Files.newDirectoryStream(
				RessourcesUnpacker.SAMPLES_PATH,
				"*.py"
			)
		) {
			for (final Path entry : stream) {
				final Path targetPath = workspace.resolve(entry.getFileName());
				Files.copy(
					entry,
					targetPath,
					StandardCopyOption.REPLACE_EXISTING
				);
			}
		} catch (IOException e) {
			throw new RuntimeException("Error copying example scripts", e);
		}

		return workspace;
	}

	public static Path getVenvDir(Path workspace) {
		return workspace.resolve(VENV_DIR);
	}

	public static Path getDefaultWorkspace() {
		return Paths
			.get(getWorkspacesDir().getAbsolutePath())
			.resolve(DEFAULT_VENV_NAME);
	}

	/**
	 * Get the scalpel configuration directory.
	 *
	 * @return The scalpel configuration directory. (default: $HOME/.scalpel)
	 */
	public static File getScalpelDir() {
		final File dir = RessourcesUnpacker.DATA_DIR_PATH.toFile();
		if (!dir.exists()) {
			dir.mkdir();
		}

		return dir;
	}

	/**
	 * Get the default venvs directory.
	 *
	 * @return The default venvs directory. (default: $HOME/.scalpel/venvs)
	 */
	public static File getWorkspacesDir() {
		final File dir = new File(getScalpelDir(), "venvs");
		if (!dir.exists()) {
			dir.mkdir();
		}

		return dir;
	}
}
