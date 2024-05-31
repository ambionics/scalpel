package lexfo.scalpel;

import com.google.common.collect.ImmutableSet;
import com.jediterm.terminal.ui.UIUtil;

/**
  Contains constants used by the extension.
*/
public class Constants {

	public static final String REQ_EDIT_PREFIX = "req_edit_";

	/**
    	Callback prefix for request editors.
	*/
	public static final String FRAMEWORK_REQ_EDIT_PREFIX =
		"_" + REQ_EDIT_PREFIX;

	public static final String RES_EDIT_PREFIX = "res_edit_";

	/**
    	Callback prefix for response editors.
	*/
	public static final String FRAMEWORK_RES_EDIT_PREFIX =
		"_" + RES_EDIT_PREFIX;

	/**
    	Callback suffix for HttpMessage-to-bytes convertion.
	*/
	public static final String IN_SUFFIX = "in";

	/**
    	Callback suffix for bytes to HttpMessage convertion.
	*/
	public static final String OUT_SUFFIX = "out";

	public static final String REQ_CB_NAME = "request";

	/**
    	Callback prefix for request intercepters.
	*/
	public static final String FRAMEWORK_REQ_CB_NAME = "_" + REQ_CB_NAME;

	public static final String RES_CB_NAME = "response";

	public static final ImmutableSet<String> VALID_HOOK_PREFIXES = ImmutableSet.of(
		REQ_EDIT_PREFIX,
		RES_EDIT_PREFIX,
		REQ_CB_NAME,
		RES_CB_NAME
	);

	/**
    	Callback prefix for response intercepters.
	*/
	public static final String FRAMEWORK_RES_CB_NAME = "_" + RES_CB_NAME;

	/**
		Scalpel prefix for the persistence databases.

		@see burp.api.montoya.persistence.Persistence
	*/
	public static final String PERSISTENCE_PREFIX = "scalpel:";

	/**
		Persistence key for the cached user script path.
	*/
	public static final String PERSISTED_SCRIPT =
		PERSISTENCE_PREFIX + "script_path";

	/**
		Persistence key for the cached framework path.
	*/
	public static final String PERSISTED_FRAMEWORK =
		PERSISTENCE_PREFIX + "framework_path";

	public static final String GET_CB_NAME = "_get_callables";

	/**
	 * Required python packages
	 */
	public static final String[] DEFAULT_VENV_DEPENDENCIES = new String[] {
		"jep==4.2.0",
	};

	public static final String[] PYTHON_DEPENDENCIES = new String[] {
		"requests",
		"requests-toolbelt",
	};

	/**
	 * Venv dir containing site-packages
	 */
	public static final String VENV_LIB_DIR = UIUtil.isWindows ? "Lib" : "lib";

	/**
	 * JEP native library filename
	 */
	public static final String NATIVE_LIBJEP_FILE = UIUtil.isWindows
		? "jep.dll"
		: UIUtil.isMac ? "libjep.jnilib" : "libjep.so";

	/**
	 * Python 3 executable filename
	 */
	public static final String PYTHON_BIN = UIUtil.isWindows
		? "python.exe"
		: "python3";

	public static final String PIP_BIN = UIUtil.isWindows ? "pip.exe" : "pip";
	public static final String VENV_BIN_DIR = UIUtil.isWindows
		? "Scripts"
		: "bin";

	public static final String DEFAULT_TERMINAL_EDITOR = "vi";

	public static final String DEFAULT_WINDOWS_EDITOR = "notepad.exe";

	public static final String EDITOR_MODE_ANNOTATION_KEY =
		"scalpel_editor_mode";
	public static final String HEX_EDITOR_MODE = "hex";
	public static final String RAW_EDITOR_MODE = "raw";
	public static final String DEFAULT_EDITOR_MODE = RAW_EDITOR_MODE;

	public static final int MIN_SUPPORTED_PYTHON_VERSION = 8;
	public static final int PREFERRED_PYTHON_VERSION = 10;

	public static final String DEFAULT_UNIX_SHELL = "/bin/bash";

	public static final String DEFAULT_LINUX_TERM_EDIT_CMD =
		CommandChecker.getAvailableCommand(
			System.getenv("EDITOR"),
			"micro",
			"vim",
			"nano",
			"vi",
			"emacs",
			"bat",
			"pager",
			"less",
			"more",
			"/bin/cat"
		) +
		" {file}";

	public static final String DEFAULT_LINUX_OPEN_FILE_CMD =
		CommandChecker.getAvailableCommand(
			"code {dir}",
			"xdg-open",
			"gnome-open",
			"kde-open",
			"exo-open",
			"mimeopen",
			"gvfs-open",
			"open",
			DEFAULT_LINUX_TERM_EDIT_CMD
		) +
		" {file}";

	public static final String DEFAULT_LINUX_OPEN_DIR_CMD =
		CommandChecker.getAvailableCommand(
			"xdg-open",
			"gnome-open",
			"kde-open",
			"exo-open",
			"mimeopen",
			"gvfs-open",
			"open"
		) +
		" {dir}";

	public static final String DEFAULT_WINDOWS_TERM_EDIT_CMD = "type {file}";
	public static final String DEFAULT_WINDOWS_OPEN_FILE_CMD =
		"explorer.exe {file}";
	public static final String DEFAULT_WINDOWS_OPEN_DIR_CMD =
		"explorer.exe {dir}";

	public static final String DEFAULT_TERM_EDIT_CMD = UIUtil.isWindows
		? DEFAULT_WINDOWS_TERM_EDIT_CMD
		: DEFAULT_LINUX_TERM_EDIT_CMD;
	public static final String DEFAULT_OPEN_FILE_CMD = UIUtil.isWindows
		? DEFAULT_WINDOWS_OPEN_FILE_CMD
		: DEFAULT_LINUX_OPEN_FILE_CMD;
	public static final String DEFAULT_OPEN_DIR_CMD = UIUtil.isWindows
		? DEFAULT_WINDOWS_OPEN_DIR_CMD
		: DEFAULT_LINUX_OPEN_DIR_CMD;
}
