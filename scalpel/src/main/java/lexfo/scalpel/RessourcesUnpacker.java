package lexfo.scalpel;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Enumeration;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/**
  Provides methods for unpacking the Scalpel resources.
*/
public class RessourcesUnpacker {

	// Scalpel configuration directory basename
	public static final String DATA_DIRNAME = ".scalpel";

	public static final Path DATA_DIR_PATH = Path.of(
		System.getProperty("user.home"),
		DATA_DIRNAME
	);
	// Directory to copy ressources embed in .jar
	public static final String RESSOURCES_DIRNAME = "extracted";

	// Directory to copy the Python stuff
	public static final String PYTHON_DIRNAME =
		"python3-" + PythonSetup.getPythonVersion();

	// Directory to copy the base init script
	public static final String SHELL_DIRNAME = "shell";

	// Directory to copy the script template to open when creating a new script
	public static final String TEMPLATES_DIRNAME = "templates";

	// Directory where user venvs will be created
	public static final String WORKSPACE_DIRNAME = "venv";

	// Whitelist for the ressources to extract
	private static final Set<String> RESSOURCES_TO_COPY = Set.of(
		PYTHON_DIRNAME,
		SHELL_DIRNAME,
		TEMPLATES_DIRNAME,
		WORKSPACE_DIRNAME
	);

	// Directory containing example scripts
	public static final String SAMPLES_DIRNAME = "samples";

	public static final String DEFAULT_SCRIPT_FILENAME = "default.py";

	// The absolute path to the Scalpel resources directory.
	public static final Path RESSOURCES_PATH = DATA_DIR_PATH.resolve(
		RESSOURCES_DIRNAME
	);

	// Actual paths for directories defined aboves

	public static final Path PYTHON_PATH = RESSOURCES_PATH.resolve(
		PYTHON_DIRNAME
	);
	public static final Path WORKSPACE_PATH = RESSOURCES_PATH.resolve(
		WORKSPACE_DIRNAME
	);

	// Path to the Pyscalpel module
	public static final Path PYSCALPEL_PATH = PYTHON_PATH.resolve("pyscalpel");

	// Path to the framework script
	public static final Path FRAMEWORK_PATH = PYSCALPEL_PATH.resolve(
		"_framework.py"
	);

	public static final Path SAMPLES_PATH = PYTHON_PATH.resolve(
		SAMPLES_DIRNAME
	);

	public static final Path DEFAULT_SCRIPT_PATH = SAMPLES_PATH.resolve(
		DEFAULT_SCRIPT_FILENAME
	);

	public static final Path BASH_INIT_FILE_PATH = RESSOURCES_PATH
		.resolve(SHELL_DIRNAME)
		.resolve("init-venv.sh");

	// https://stackoverflow.com/questions/320542/how-to-get-the-path-of-a-running-jar-file#:~:text=return%20new%20File(MyClass.class.getProtectionDomain().getCodeSource().getLocation()%0A%20%20%20%20.toURI()).getPath()%3B
	/**
	    Returns the path to the Scalpel JAR file.
	    @return The path to the Scalpel JAR file.
	*/
	private static String getRunningJarPath() {
		try {
			return Scalpel.class.getProtectionDomain()
				.getCodeSource()
				.getLocation()
				.toURI()
				.getPath();
		} catch (Throwable e) {
			return "err";
		}
	}

	// https://stackoverflow.com/questions/9324933/what-is-a-good-java-library-to-zip-unzip-files#:~:text=Extract%20zip%20file%20and%20all%20its%20subfolders%2C%20using%20only%20the%20JDK%3A
	/**
	    Extracts the Scalpel python resources from the Scalpel JAR file.

	    @param zipFile The path to the Scalpel JAR file.
	    @param extractFolder The path to the Scalpel resources directory.
	*/
	private static void extractRessources(
		String zipFile,
		String extractFolder,
		Set<String> entriesWhitelist
	) {
		ZipFile zip = null;
		try {
			final int BUFFER = 2048;
			final File file = new File(zipFile);
			zip = new ZipFile(file);

			final String newPath = extractFolder;

			new File(newPath).mkdirs();
			final Enumeration<? extends ZipEntry> zipFileEntries = zip.entries();

			// Process each entry
			while (zipFileEntries.hasMoreElements()) {
				// grab a zip file entry
				final ZipEntry entry = zipFileEntries.nextElement();

				final String currentEntry = entry.getName();
				final long size = entry.getSize();

				if (
					entriesWhitelist
						.stream()
						.noneMatch(currentEntry::startsWith)
				) {
					continue;
				}

				ScalpelLogger.info(
					"Extracting " + currentEntry + " (" + size + " bytes)"
				);

				final File destFile = new File(newPath, currentEntry);
				final File destinationParent = destFile.getParentFile();

				// create the parent directory structure if needed
				destinationParent.mkdirs();

				if (!entry.isDirectory()) {
					final InputStream is = zip.getInputStream(entry);

					int currentByte;
					// establish buffer for writing file
					final byte[] data = new byte[BUFFER];

					// write the current file to disk
					final FileOutputStream dest = new FileOutputStream(
						destFile
					);

					// read and write until last byte is encountered
					while ((currentByte = is.read(data)) != -1) {
						dest.write(data, 0, currentByte);
					}
					dest.flush();
					dest.close();
					is.close();
				}
			}
		} catch (Throwable e) {
			ScalpelLogger.logStackTrace(e);
		} finally {
			try {
				if (zip != null) zip.close();
			} catch (Throwable e) {
				ScalpelLogger.logStackTrace(e);
			}
		}
	}

	/**
	    Initializes the Scalpel resources directory.
	*/
	public static void extractRessourcesToHome() {
		try {
			// Create a $HOME/.scalpel/extracted directory.
			ScalpelLogger.all("Extracting to " + RESSOURCES_PATH);

			extractRessources(
				getRunningJarPath(),
				RESSOURCES_PATH.toString(),
				RESSOURCES_TO_COPY
			);

			ScalpelLogger.all(
				"Successfully extracted running .jar to " + RESSOURCES_PATH
			);
		} catch (Throwable e) {
			ScalpelLogger.error("extractRessourcesToHome() failed.");
			ScalpelLogger.logStackTrace(e);
		}
	}
}
