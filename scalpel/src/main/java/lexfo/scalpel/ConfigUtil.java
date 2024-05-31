package lexfo.scalpel;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.File;
import java.lang.reflect.Field;
import java.util.Map;

public class ConfigUtil {

	public static <T> T readConfigFile(File file, Class<T> clazz) {
		final T defaultInstance;
		try {
			defaultInstance = clazz.getDeclaredConstructor().newInstance();
		} catch (Exception e) {
			throw new RuntimeException(e);
		}

		final Map<String, Object> map = IO.readJSON(
			file,
			new TypeReference<Map<String, Object>>() {},
			e ->
				ScalpelLogger.logStackTrace(
					"/!\\ Invalid JSON config file /!\\" +
					", try re-installing Scalpel by removing ~/.scalpel and restarting Burp.",
					e
				)
		);

		if (map != null) {
			mergeWithDefaults(defaultInstance, map);
		}

		return defaultInstance;
	}

	private static <T> void mergeWithDefaults(
		T instance,
		Map<String, Object> map
	) {
		for (final Field field : instance.getClass().getDeclaredFields()) {
			field.setAccessible(true);
			if (map.containsKey(field.getName())) {
				try {
					field.set(instance, map.get(field.getName()));
				} catch (IllegalAccessException e) {
					throw new RuntimeException(e);
				}
			}
		}
	}
}
