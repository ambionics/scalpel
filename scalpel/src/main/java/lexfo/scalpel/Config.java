package lexfo.scalpel;

import burp.api.montoya.MontoyaApi;
import burp.api.montoya.persistence.PersistedObject;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.jediterm.terminal.ui.UIUtil;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Stream;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import lexfo.scalpel.ScalpelLogger.Level;

/**
 * Scalpel configuration.
 *
 *
 *  By default, the project configuration file is located in the $HOME/.scalpel directory.
 *
 *  The file name is the project id with the .json extension.
 *  The project ID is an UUID stored in the extension data:
 *  https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/persistence/Persistence.html#extensionData()
 *
 *  The configuration file looks something like this:
 *  {
 *      "workspacePaths": [
 *          "/path/to/workspace1",
 *          "/path/to/workspace2"
 *      ],
 *      "scriptPath": "/path/to/script.py",
 *  }
 *
 *  The file is not really designed to be directly edited by the user, but rather by the extension itself.
 *
 *  A configuration file is needed because we need to store global persistent data arrays. (e.g. workspacePaths)
 *  Which can't be done with the Java Preferences API.
 *  Furthermore, it's simply more convenient to store as JSON and we already have a scalpel directory to store 'ad-hoc' python workspaces.
 */
public class Config {

	/**
	 * Global configuration.
	 *
	 * This is the configuration that is shared between all projects.
	 * It contains the list of venvs and the default values.
	 *
	 * The default values are inferred from the user behavior.
	 * For a new project, the default venv, script and framework paths are the last ones selected by the user in any different project.
	 * If the user has never selected a venv, script or framework, it is set to default values.
	 */
	public static class _GlobalData {

		/**
		 * List of registered venv paths.
		 */
		public ArrayList<String> workspacePaths = new ArrayList<>();
		public String defaultWorkspacePath = "";
		public String defaultScriptPath = "";
		public String jdkPath = null;
		public String logLevel = "INFO";
		public String openScriptCommand = Constants.DEFAULT_OPEN_FILE_CMD;
		public String editScriptCommand = Constants.DEFAULT_TERM_EDIT_CMD;
		public String openFolderCommand = Constants.DEFAULT_OPEN_DIR_CMD;
		public boolean enabled = true;
	}

	// Persistent data for a specific project.
	public static class _ProjectData {

		/*
		 * The venv to run the script in.
		 */
		public String workspacePath = "";

		/*
		 * The script to run.
		 */
		public String userScriptPath = "";

		public String displayProxyErrorPopup = "True";
	}

	private final _GlobalData globalConfig;
	private final _ProjectData projectConfig;
	private long lastModified = System.currentTimeMillis();

	// Scalpel configuration file extension
	private static final String CONFIG_EXT = ".json";

	// UUID generated to identify the project (because the project name cannot be fetched)
	// This is stored in the extension data which is specific to the project.
	public final String projectID;

	// Path to the project configuration file
	private final File projectScalpelConfig;

	// Prefix for the extension data keys
	private static final String DATA_PREFIX = "scalpel.";

	// Key for the project ID
	private static final String DATA_PROJECT_ID_KEY = DATA_PREFIX + "projectID";

	private Path _jdkPath = null;

	private static Config instance = null;

	private final MontoyaApi API;

	private Config(final MontoyaApi API) throws IOException {
		instance = this;

		this.API = API;

		final PersistedObject extensionData = API.persistence().extensionData();
		this.projectID =
			Optional
				.ofNullable(extensionData.getString(DATA_PROJECT_ID_KEY))
				.orElseGet(() -> {
					String id = UUID.randomUUID().toString();
					extensionData.setString(DATA_PROJECT_ID_KEY, id);
					return id;
				});

		// Set the path to the project configuration file
		this.projectScalpelConfig =
			RessourcesUnpacker.DATA_DIR_PATH
				.resolve(projectID + CONFIG_EXT)
				.toFile();

		this.globalConfig = initGlobalConfig();
		this._jdkPath = Path.of(this.globalConfig.jdkPath);

		// Load project config or create a new one on failure. (e.g. file doesn't exist)
		this.projectConfig = this.initProjectConfig();
		saveAllConfig();
	}

	/**
	 * Provides access to the singleton instance of the Config class.
	 *
	 * @return The single instance of the Config class.
	 */
	private static synchronized Config getInstance(
		final Optional<MontoyaApi> optAPI
	) {
		if (instance == null) {
			try {
				final MontoyaApi api = optAPI.orElseThrow(() ->
					new RuntimeException(
						"Config was not initialized with the MontoyaAPI"
					)
				);

				instance = new Config(api);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
		}
		return instance;
	}

	/**
	 * Provides access to the singleton instance of the Config class.
	 * The config must already be initialized to use this.
	 *
	 * @return The single instance of the Config class.
	 */
	public static synchronized Config getInstance() {
		return getInstance(Optional.empty());
	}

	/**
	 * Provides access to the singleton instance of the Config class.
	 *
	 * @return The single instance of the Config class.
	 */
	public static synchronized Config getInstance(final MontoyaApi API) {
		return getInstance(Optional.of(API));
	}

	private static <T> T readConfigFile(File file, Class<T> clazz) {
		return IO.readJSON(
			file,
			clazz,
			e ->
				ScalpelLogger.logStackTrace(
					"/!\\ Invalid JSON config file /!\\" +
					", try re-installing Scalpel by removing ~/.scalpel and restarting Burp.",
					e
				)
		);
	}

	private _GlobalData initGlobalConfig() throws IOException {
		// Load global config file
		final File globalConfigFile = getGlobalConfigFile();

		// If config file does not exist, return default global data
		if (!globalConfigFile.exists()) {
			return getDefaultGlobalData();
		}

		// Read existing configuration
		final _GlobalData globalData = ConfigUtil.readConfigFile(
			globalConfigFile,
			_GlobalData.class
		);

		// Remove workspace paths that do not exist anymore
		globalData.workspacePaths.removeIf(path -> !new File(path).exists());

		// Set JDK path if it's not set
		if (globalData.jdkPath == null) {
			globalData.jdkPath = findJdkPath().toString();
		}

		// Ensure there is at least one workspace path
		if (globalData.workspacePaths.isEmpty()) {
			globalData.workspacePaths.add(
				Workspace
					.getOrCreateDefaultWorkspace(Path.of(globalData.jdkPath))
					.toString()
			);
		}

		// Set the default workspace path
		if (
			globalData.defaultWorkspacePath == null ||
			!new File(globalData.defaultWorkspacePath).exists()
		) {
			globalData.defaultWorkspacePath = globalData.workspacePaths.get(0);
		}

		// Set log level
		API
			.persistence()
			.preferences()
			.setString("logLevel", globalData.logLevel);
		ScalpelLogger.setLogLevel(globalData.logLevel);

		return globalData;
	}

	private _ProjectData initProjectConfig() {
		return Optional
			.of(projectScalpelConfig)
			.filter(File::exists)
			.map(file -> ConfigUtil.readConfigFile(file, _ProjectData.class))
			.map(d -> {
				d.workspacePath =
					Optional
						.ofNullable(d.workspacePath) // Ensure the venv path is set.
						.filter(p -> globalConfig.workspacePaths.contains(p)) // Ensure the selected venv is registered.
						.orElse(globalConfig.defaultWorkspacePath); // Otherwise, use the default venv.
				return d;
			})
			.orElseGet(this::getDefaultProjectData);
	}

	/**
	 * Write the global configuration to the global configuration file.
	 */
	private synchronized void saveGlobalConfig() {
		IO.writeJSON(getGlobalConfigFile(), globalConfig);
	}

	/**
	 * Write the project configuration to the project configuration file.
	 */
	private synchronized void saveProjectConfig() {
		this.lastModified = System.currentTimeMillis();
		IO.writeJSON(projectScalpelConfig, projectConfig);
	}

	/**
	 * Write the global and project configuration to their respective files.
	 */
	private synchronized void saveAllConfig() {
		saveGlobalConfig();
		saveProjectConfig();
	}

	/**
	 * Get the last modification time of the project configuration file.
	 *
	 * This is used to reload the execution configuration when the project configuration file is modified.
	 * @return The last modification time of the project configuration file.
	 */
	public long getLastModified() {
		return lastModified;
	}

	/**
	 * Get the global configuration file.
	 *
	 * @return The global configuration file. (default: $HOME/.scalpel/global.json)
	 */
	public static File getGlobalConfigFile() {
		return RessourcesUnpacker.DATA_DIR_PATH
			.resolve("global" + CONFIG_EXT)
			.toFile();
	}

	private static boolean hasIncludeDir(Path jdkPath) {
		File inc = jdkPath.resolve("include").toFile();
		return inc.exists() && inc.isDirectory();
	}

	private static Optional<Path> guessJdkPath() throws IOException {
		if (UIUtil.isWindows) {
			// Official JDK usually gets installed in 'C:\\Program Files\\Java\\jdk-<version>'
			final Path winJdkPath = Path.of("C:\\Program Files\\Java\\");
			try (Stream<Path> files = Files.walk(winJdkPath)) {
				return files
					.filter(f -> f.toFile().getName().contains("jdk"))
					.map(Path::toAbsolutePath)
					.filter(Config::hasIncludeDir)
					.findFirst();
			} catch (NoSuchFileException e) {
				ScalpelLogger.warn(
					"Could not find JDK in common Windows location (" +
					winJdkPath +
					"), prompting the user to select it instead.."
				);
				return Optional.empty();
			}
		}

		if (UIUtil.isMac) {
			// Get output of /usr/libexec/java_home
			final String javaHomeCommand = "/usr/libexec/java_home";
			try {
				final Process process = Runtime
					.getRuntime()
					.exec(javaHomeCommand);

				try (
					final BufferedReader reader = new BufferedReader(
						new InputStreamReader(process.getInputStream())
					)
				) {
					final String jdkPathStr = reader.readLine();
					if (jdkPathStr != null && !jdkPathStr.isBlank()) {
						final Path macJdkPath = Path.of(jdkPathStr);
						if (hasIncludeDir(macJdkPath)) {
							return Optional.of(macJdkPath);
						}
					}
				}
			} catch (IOException e) {
				ScalpelLogger.error(
					"Could not execute " + javaHomeCommand + " :"
				);
				ScalpelLogger.logStackTrace(e);
			}
		}

		// We try to find the JDK from the javac binary path
		final String binaryName = "javac";
		final Stream<Path> matchingBinaries = findBinaryInPath(binaryName);
		final Stream<Path> potentialJdkPaths = matchingBinaries
			.map(binaryPath -> {
				try {
					final Path absolutePath = binaryPath.toRealPath();
					return absolutePath.getParent().getParent();
				} catch (IOException e) {
					return null;
				}
			})
			.filter(Objects::nonNull);

		// Some distributions (e.g. Kali) come with an incomplete JDK and requires installing a package for the complete one.
		// This filter prevents selecting those.
		final Stream<Path> validJavaHomes = potentialJdkPaths.filter(
			Config::hasIncludeDir
		);

		return validJavaHomes.findFirst();
	}

	/**
	 * Tries to get the JDK path from PATH, usual install locations, or by prompting the user.
	 * @return The JDK path.
	 * @throws IOException
	 */
	public Path findJdkPath() throws IOException {
		if (_jdkPath != null) {
			// Return memoized path
			return _jdkPath;
		}

		final Path javaHome = guessJdkPath()
			.orElseGet(() -> {
				// Display popup telling the user that JDK was not found and needs to select it manually
				JOptionPane.showMessageDialog(
					null,
					"JDK not found. Please select JDK path manually.",
					"JDK not found",
					JOptionPane.INFORMATION_MESSAGE
				);

				// Include a filechooser to choose the path
				final JFileChooser fileChooser = new JFileChooser();
				fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);

				final int option = fileChooser.showOpenDialog(null);
				if (option == JFileChooser.APPROVE_OPTION) {
					final File file = fileChooser.getSelectedFile();
					return file.toPath();
				}
				return null;
			});

		if (javaHome == null) {
			throw new RuntimeException(
				"No JDK was found nor manually selected, please install a JDK in a common place"
			);
		}
		// Memoize path
		_jdkPath = javaHome;

		return javaHome;
	}

	private static Stream<Path> findBinaryInPath(String binaryName) {
		final String systemPath = System.getenv("PATH");
		final String[] pathDirs = systemPath.split(
			System.getProperty("path.separator")
		);

		return Arrays
			.stream(pathDirs)
			.map(pathDir -> Paths.get(pathDir, binaryName))
			.filter(Files::exists)
			.map(path -> {
				try {
					return path.toRealPath();
				} catch (IOException e) {
					return path;
				}
			});
	}

	/**
	 * Get the global configuration.
	 *
	 * @return The global configuration.
	 */
	private _GlobalData getDefaultGlobalData() throws IOException {
		final _GlobalData data = new _GlobalData();

		data.jdkPath = IO.ioWrap(this::findJdkPath).toString();

		data.defaultScriptPath =
			RessourcesUnpacker.DEFAULT_SCRIPT_PATH.toString();

		RessourcesUnpacker.FRAMEWORK_PATH.toString();

		data.workspacePaths = new ArrayList<>();

		data.workspacePaths.add(
			Workspace
				.getOrCreateDefaultWorkspace(Path.of(data.jdkPath))
				.toString()
		);

		data.defaultWorkspacePath = data.workspacePaths.get(0);
		return data;
	}

	/**
	 * Get the project configuration.
	 *
	 * @return The project configuration.
	 */
	private _ProjectData getDefaultProjectData() {
		final _ProjectData data = new _ProjectData();

		data.userScriptPath = globalConfig.defaultScriptPath;
		data.workspacePath = globalConfig.defaultWorkspacePath;
		return data;
	}

	// Getters

	/*
	 * Get the venv paths list.
	 *
	 * @return The venv paths list.
	 */
	public String[] getVenvPaths() {
		return globalConfig.workspacePaths.toArray(new String[0]);
	}

	/*
	 * Get the selected user script path.
	 *
	 * @return The selected user script path.
	 */
	public Path getUserScriptPath() {
		return Path.of(projectConfig.userScriptPath);
	}

	/*
	 * Get the selected framework path.
	 *
	 * @return The selected framework path.
	 */
	public Path getFrameworkPath() {
		return RessourcesUnpacker.FRAMEWORK_PATH;
	}

	public Path getJdkPath() {
		return Path.of(globalConfig.jdkPath);
	}

	/*
	 * Get the selected venv path.
	 *
	 * @return The selected venv path.
	 */
	public Path getSelectedWorkspacePath() {
		return Path.of(projectConfig.workspacePath);
	}

	// Setters

	public void setJdkPath(Path path) {
		this.globalConfig.jdkPath = path.toString();
		this.saveGlobalConfig();
	}

	/*
	 * Set the venv paths list.
	 * Saves the new list to the global configuration file.
	 *
	 * @param venvPaths The new venv paths list.
	 */
	public void setVenvPaths(ArrayList<String> venvPaths) {
		this.globalConfig.workspacePaths = venvPaths;
		this.saveGlobalConfig();
	}

	/*
	 * Set the selected user script path.
	 * Saves the new path to the global and project configuration files.
	 *
	 * @param scriptPath The new user script path.
	 */
	public void setUserScriptPath(Path scriptPath) {
		this.projectConfig.userScriptPath = scriptPath.toString();
		this.globalConfig.defaultScriptPath = scriptPath.toString();
		this.saveAllConfig();
	}

	/*
	 * Set the selected venv path.
	 * Saves the new path to the global and project configuration files.
	 *
	 * @param venvPath The new venv path.
	 */
	public void setSelectedVenvPath(Path venvPath) {
		this.projectConfig.workspacePath = venvPath.toString();
		this.globalConfig.defaultWorkspacePath = venvPath.toString();
		this.saveAllConfig();
	}

	// Methods

	/*
	 * Add a venv path to the list.
	 * Saves the new list to the global configuration file.
	 *
	 * @param venvPath The venv path to add.
	 */
	public void addVenvPath(Path venvPath) {
		globalConfig.workspacePaths.add(venvPath.toString());
		this.saveGlobalConfig();
	}

	/*
	 * Remove a venv path from the list.
	 * Saves the new list to the global configuration file.
	 *
	 * @param venvPath The venv path to remove.
	 */
	public void removeVenvPath(Path venvPath) {
		globalConfig.workspacePaths.remove(venvPath.toString());
		this.saveGlobalConfig();
	}

	public String getLogLevel() {
		return globalConfig.logLevel;
	}

	public void setLogLevel(String logLevel) {
		API.persistence().preferences().setString("logLevel", logLevel);
		ScalpelLogger.setLogLevel(Level.nameToLevel.get(logLevel));

		this.globalConfig.logLevel = logLevel;
		saveGlobalConfig();
	}

	public String getOpenScriptCommand() {
		return globalConfig.openScriptCommand;
	}

	public void setOpenScriptCommand(String openScriptCommand) {
		this.globalConfig.openScriptCommand = openScriptCommand;
		saveGlobalConfig();
	}

	public String getEditScriptCommand() {
		return globalConfig.editScriptCommand;
	}

	public void setEditScriptCommand(String editScriptCommand) {
		this.globalConfig.editScriptCommand = editScriptCommand;
		saveGlobalConfig();
	}

	public String getOpenFolderCommand() {
		return globalConfig.openFolderCommand;
	}

	public void setOpenFolderCommand(String openFolderCommand) {
		this.globalConfig.openFolderCommand = openFolderCommand;
		saveGlobalConfig();
	}

	/*
	 * Get the display proxy error popup status. (enabled/disabled)
	 *
	 * @return The current status of proxy error popup display.
	 */
	public String getDisplayProxyErrorPopup() {
		return projectConfig.displayProxyErrorPopup;
	}

	/*
	 * Set the display proxy error popup status.
	 * Saves the new status to the project configuration file.
	 *
	 * @param displayProxyErrorPopup The new status for displaying proxy error popups.
	 */
	public void setDisplayProxyErrorPopup(String displayProxyErrorPopup) {
		this.projectConfig.displayProxyErrorPopup = displayProxyErrorPopup;
		saveProjectConfig();
	}

	/*
	 * Get the enabled status.
	 *
	 * @return The current enabled status.
	 */
	public boolean isEnabled() {
		return globalConfig.enabled;
	}

	/*
	 * Set the enabled status.
	 * Saves the new status to the global configuration file.
	 *
	 * @param enabled The new enabled status.
	 */
	public void setEnabled(boolean enabled) {
		this.globalConfig.enabled = enabled;
		saveGlobalConfig();
	}

	public String dumpConfig() {
		// Dump whole config as string for debugging
		final ObjectWriter writer = new ObjectMapper()
			.writerWithDefaultPrettyPrinter();

		try {
			String globalConfigJSON = writer.writeValueAsString(globalConfig);
			String projectConfigJSON = writer.writeValueAsString(projectConfig);

			return (
				"Global config: \n" +
				globalConfigJSON +
				"\n------------------------\n" +
				"Project config: \n" +
				projectConfigJSON
			);
		} catch (JsonProcessingException e) {
			ScalpelLogger.logStackTrace(e);
		}
		return "";
	}
}
