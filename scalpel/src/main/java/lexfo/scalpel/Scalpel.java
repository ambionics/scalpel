package lexfo.scalpel;

import burp.api.montoya.BurpExtension;
import burp.api.montoya.MontoyaApi;
import com.jediterm.terminal.ui.UIUtil;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.stream.Collectors;
import jep.MainInterpreter;

// Burp will auto-detect and load any class that extends BurpExtension.
/**
  The main class of the extension.
  This class is instantiated by Burp Suite and is used to initialize the extension.
*/
public class Scalpel implements BurpExtension {

	/**
	 * The ScalpelExecutor object used to execute Python scripts.
	 */
	private ScalpelExecutor executor;

	/**
	 * The MontoyaApi object used to interact with Burp Suite.
	 */
	private MontoyaApi API;

	private Config config;

	private static void logConfig(final Config config) {
		ScalpelLogger.all("Config:");
		ScalpelLogger.all("Framework: " + config.getFrameworkPath());
		ScalpelLogger.all("Script: " + config.getUserScriptPath());
		ScalpelLogger.all(
			"Venvs: " +
			Arrays
				.stream(config.getVenvPaths())
				.collect(Collectors.joining("\",\"", "[\"", "\"]"))
		);
		ScalpelLogger.all("Default venv: " + Workspace.getDefaultWorkspace());
		ScalpelLogger.all(
			"Selected venv: " + config.getSelectedWorkspacePath()
		);
	}

	private static void setupJepFromConfig(Config config) throws IOException {
		final Path venvPath = Workspace
			.getOrCreateDefaultWorkspace(config.getJdkPath())
			.resolve(Workspace.VENV_DIR);

		final File dir = Venv.getSitePackagesPath(venvPath).toFile();

		final File[] jepDirs = dir.listFiles((__, name) -> name.matches("jep"));

		if (jepDirs.length == 0) {
			throw new IOException(
				"FATAL: Could not find jep directory in " +
				dir +
				"\nIf the install failed previously, remove the ~/.scalpel directory and reload the extension"
			);
		}

		final String jepDir = jepDirs[0].getAbsolutePath();

		// Adding path to java.library.path is necessary for Windows
		final String oldLibPath = System.getProperty("java.library.path");
		final String newLibPath = jepDir + File.pathSeparator + oldLibPath;
		System.setProperty("java.library.path", newLibPath);

		final String libjepFile = Constants.NATIVE_LIBJEP_FILE;
		final String jepLib = Paths.get(jepDir, libjepFile).toString();

		// Load the library ourselves to catch errors right away.
		ScalpelLogger.all("Loading Jep native library from " + jepLib);
		System.load(jepLib);
		MainInterpreter.setJepLibraryPath(jepLib);
	}

	private static void waitForExecutor(
		MontoyaApi API,
		ScalpelEditorProvider provider,
		ScalpelExecutor executor
	) {
		while (executor.isStarting()) {
			IO.sleep(100);
		}
		if (executor.isRunning()) {
			ScalpelLogger.all(
				"SUCCESS: Initialized Scalpel's embedded Python successfully!"
			);
		} else {
			ScalpelLogger.error(
				"ERROR: Failed to initialize Scalpel's embedded Python."
			);
		}

		// Init may fail if the user script is invalid.
		// Wait for the user to fix their script before registering Burp hooks.
		while (!executor.isRunning()) {
			IO.sleep(100);
		}
		// Add editor tabs to Burp
		API.userInterface().registerHttpRequestEditorProvider(provider);
		API.userInterface().registerHttpResponseEditorProvider(provider);

		// Intercept HTTP requests
		API
			.http()
			.registerHttpHandler(
				new ScalpelHttpRequestHandler(API, provider, executor)
			);
	}

	/**
     * Initializes the extension.
    @param API The MontoyaApi object to use.
	*/
	@Override
	public void initialize(MontoyaApi API) {
		this.API = API;

		// Set displayed extension name.
		API.extension().setName("Scalpel");

		// Create a logger that will display messages in Burp extension logs.
		ScalpelLogger.setLogger(API.logging());
		final String logLevel = API
			.persistence()
			.preferences()
				.getString("logLevel");

		if (logLevel != null) {
			ScalpelLogger.setLogLevel(logLevel);
		}

		try {
			ScalpelLogger.all("Initializing...");

			if (UIUtil.isMac) {
				// It may be required to manually load libpython on MacOS for jep not to break
				// https://github.com/ninia/jep/issues/432#issuecomment-1317590878
				PythonSetup.loadLibPython3();
			}

			// Extract embeded ressources.
			ScalpelLogger.all("Extracting ressources...");
			RessourcesUnpacker.extractRessourcesToHome();

			ScalpelLogger.all("Reading config and initializing venvs...");
			ScalpelLogger.all(
				"(This might take a minute, Scalpel is installing dependencies...)"
			);

			config = Config.getInstance(API);
			logConfig(config);

			setupJepFromConfig(config);

			// Initialize Python task queue.
			executor = new ScalpelExecutor(API, config);

			// Add the configuration tab to Burp UI.
			API
				.userInterface()
				.registerSuiteTab(
					"Scalpel",
					UIBuilder.constructConfigTab(
						API,
						executor,
						config,
						API.userInterface().currentTheme()
					)
				);

			// Create the provider responsible for creating the request/response editors for Burp.
			final ScalpelEditorProvider provider = new ScalpelEditorProvider(
				API,
				executor
			);

			// Inject dependency to solve circular dependency.
			executor.setEditorsProvider(provider);

			// Extension is fully loaded.
			ScalpelLogger.all("Successfully loaded scalpel.");

			// Log an error or success message when executor has finished initializing.
			Async.run(() -> waitForExecutor(API, provider, executor));
		} catch (Throwable e) {
			ScalpelLogger.all("Failed to initialize Scalpel:");
			if (
				e instanceof ExceptionInInitializerError && e.getCause() != null
			) {
				// Log the original error and stacktrace
				// This happens when an Exception is thrown in the static initialization of RessourcesUnpacker
				e = e.getCause();
			}

			ScalpelLogger.logFatalStackTrace(e);

			// Burp race-condition: cannot unload an extension while in initialize()
			Async.run(() -> {
				IO.sleep(500);
				API.extension().unload();
			});
		}
	}
}
