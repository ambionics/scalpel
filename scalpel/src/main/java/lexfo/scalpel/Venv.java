package lexfo.scalpel;

import com.jediterm.terminal.ui.UIUtil;
import java.io.BufferedReader;
/**
 * The Venv class is used to manage Python virtual environments.
 */
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.commons.lang3.ArrayUtils;

/**
 * Manage Python virtual environments.
 */
public class Venv {

	/**
	 * Create a virtual environment.
	 *
	 * @param path The path to the virtual environment directory.
	 * @return The finished process of the "python3 -m venv" command.
	 */
	public static Process create(Path path)
		throws IOException, InterruptedException {
		// Create the directory for the virtual environment
		Files.createDirectories(path);

		// Create the virtual environment using the "python3 -m venv" command
		final ProcessBuilder processBuilder = new ProcessBuilder(
			Constants.PYTHON_BIN,
			"-m",
			"venv",
			path.toString()
		);

		processBuilder.redirectErrorStream(true);

		final Process process = processBuilder.start();

		// Wait for the virtual environment creation to complete
		process.waitFor();

		return process;
	}

	// https://github.com/ninia/jep/issues/495
	private static void clearPipCache(Path venv)
		throws IOException, InterruptedException {
		final ProcessBuilder cacheClearProcessBuilder = new ProcessBuilder(
			getPipPath(venv).toString(),
			"cache",
			"remove",
			"jep"
		);
		final Process cacheClearProcess = cacheClearProcessBuilder.start();
		cacheClearProcess.waitFor();
		if (cacheClearProcess.exitValue() != 0) {
			ScalpelLogger.error("Failed to clear the pip cache for jep");
		}
	}

	public static Process installDefaults(
		Path venv,
		Map<String, String> env,
		Boolean installJep
	) throws IOException, InterruptedException {
		// Install the default packages

		final String[] javaDeps = Constants.DEFAULT_VENV_DEPENDENCIES;
		// Dependencies required for Java to initiate a Python interpreter (jep)

		// Dependencies required by the Scalpel Python library.
		final String[] scriptDeps = Constants.PYTHON_DEPENDENCIES;

		final String[] pkgsToInstall;
		if (installJep) {
			clearPipCache(venv);
			pkgsToInstall = ArrayUtils.addAll(javaDeps, scriptDeps);
		} else {
			pkgsToInstall = scriptDeps;
		}

		return install_background(venv, env, pkgsToInstall);
	}

	public static Process installDefaults(Path path)
		throws IOException, InterruptedException {
		// Install the default packages
		return installDefaults(path, Map.of(), true);
	}

	/**
	 * Create a virtual environment and install the default packages.
	 *
	 * @param venv The path to the virtual environment directory.
	 * @return The exit code of the "pip install ..." command.
	 */
	public static Process createAndInstallDefaults(Path venv)
		throws IOException, InterruptedException {
		// Create the virtual environment
		final Process proc = create(venv);
		if (proc.exitValue() != 0) {
			return proc;
		}
		return installDefaults(venv);
	}

	/**
	 * Delete a virtual environment.
	 *
	 * @param venv The path to the virtual environment directory.
	 */
	public static void delete(Path venv) {
		try {
			// Delete the virtual environment directory
			Files.delete(venv);
			// Return 0 (success)
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}

	/**
	 * Install a package in a virtual environment in a new thread.
	 *
	 * @param path The path to the virtual environment directory.
	 * @param pkgs The name of the package to install.
	 * @return The exit code of the "pip install ..." command.
	 */
	public static Thread install_background(Path path, String... pkgs) {
		Thread thread = new Thread(() -> IO.ioWrap(() -> install(path, pkgs)));
		thread.start();
		return thread;
	}

	/**
	 * Install a package in a virtual environment.
	 *
	 * @param path The path to the virtual environment directory.
	 * @param pkgs The name of the package to install.
	 * @return The exit code of the "pip install ..." command.
	 */
	public static Process install(Path path, String... pkgs)
		throws IOException {
		return install(path, Map.of(), pkgs);
	}

	/**
	 * Install a package in a virtual environment.
	 *
	 * @param path The path to the virtual environment directory.
	 * @param env The environnement variables to pass
	 * @param pkgs The name of the package to install.
	 * @return The exit code of the "pip install ..." command.
	 */
	public static Process install_background(
		Path path,
		Map<String, String> env,
		String... pkgs
	) throws IOException {
		// Install the package using the "pip install" command

		final LinkedList<String> command = new LinkedList<>(
			List.of(getPipPath(path).toString(), "install")
		);
		command.addAll(Arrays.asList(pkgs));

		final ProcessBuilder processBuilder = new ProcessBuilder(command);
		processBuilder.directory(path.toFile());
		processBuilder.environment().putAll(env);
		processBuilder.redirectErrorStream(true);

		final Process process = processBuilder.start();

		ScalpelLogger.debug(
			"Launched " + command.stream().collect(Collectors.joining(" "))
		);

		return process;
	}

	/**
	 * Install a package in a virtual environment.
	 *
	 * @param path The path to the virtual environment directory.
	 * @param env The environnement variables to pass
	 * @param pkgs The name of the package to install.
	 * @return The exit code of the "pip install ..." command.
	 */
	public static Process install(
		Path path,
		Map<String, String> env,
		String... pkgs
	) throws IOException {
		final Process proc = install_background(path, env, pkgs);

		final BufferedReader stdout = proc.inputReader();
		while (proc.isAlive()) {
			ScalpelLogger.all(stdout.readLine());
		}

		return proc;
	}

	protected static final class PackageInfo {

		public String name;
		public String version;
	}

	public static Path getSitePackagesPath(Path venvPath) throws IOException {
		if (UIUtil.isWindows) {
			// Find the sites-package directory path as in: <path>/Lib/site-packages
			return Files
				.walk(venvPath)
				.filter(Files::isDirectory)
				.filter(p -> p.getFileName().toString().equalsIgnoreCase("lib"))
				.map(p -> p.resolve("site-packages"))
				.filter(Files::exists)
				.findFirst()
				.orElseThrow(() ->
					new RuntimeException(
						"Failed to find venv site-packages.\n" +
						"Make sure dependencies are correctly installed. (python3,pip,venv,jdk)"
					)
				);
		}
		// Find the sites-package directory path as in: <path>/lib/python*/site-packages
		return Files
			.walk(venvPath.resolve("lib"))
			.filter(Files::isDirectory)
			.filter(p -> p.getFileName().toString().startsWith("python"))
			.map(p -> p.resolve("site-packages"))
			.filter(Files::exists)
			.findFirst()
			.orElseThrow(() ->
				new RuntimeException(
					"Failed to find venv site-packages.\n" +
					"Make sure dependencies are correctly installed. (python3,pip,venv,jdk)"
				)
			);
	}

	public static Path getExecutablePath(Path venvPath, String filename)
		throws IOException {
		final String binDir = Constants.VENV_BIN_DIR;

		return Files
			.walk(venvPath)
			.filter(Files::isDirectory)
			.filter(p -> p.getFileName().toString().equalsIgnoreCase(binDir))
			.map(p -> p.resolve(filename))
			.filter(Files::exists)
			.map(Path::toAbsolutePath)
			.findFirst()
			.orElseThrow(() ->
				new RuntimeException(
					"Failed to find " +
					filename +
					" in " +
					venvPath +
					" .\n" +
					"Make sure dependencies are correctly installed. (python3,pip,venv,jdk)"
				)
			);
	}

	public static Path getPipPath(Path venvPath) throws IOException {
		return getExecutablePath(venvPath, Constants.PIP_BIN);
	}

	/**
	 * Get the list of installed packages in a virtual environment.
	 *
	 * @param path The path to the virtual environment directory.
	 * @return The list of installed packages.
	 */
	public static PackageInfo[] getInstalledPackages(Path path)
		throws IOException {
		final ProcessBuilder processBuilder = new ProcessBuilder(
			getPipPath(path).toString(),
			"list",
			"--format",
			"json",
			"--exclude",
			"pip",
			"--exclude",
			"setuptools"
		);

		// Launch and parse the JSON output using Jackson
		final Process process = processBuilder.start();

		// Read the JSON output
		final String jsonData = new String(
			process.getInputStream().readAllBytes()
		);

		// Parse the JSON output
		return IO.readJSON(jsonData, PackageInfo[].class);
	}
}
