package lexfo.scalpel;

import java.util.HashSet;

public class UnObfuscator {

	/**
	 * Finds a Montoya interface in the specified class, its superclasses or
	 * interfaces, and return its name. Otherwise, returns the name of the class
	 * of the object.
	 */
	public static String getClassName(Object obj) {
		if (obj == null) return "null";
		HashSet<Class<?>> visited = new HashSet<Class<?>>();
		Class<?> c = obj.getClass();
		String itf = findMontoyaInterface(c, visited);
		if (itf != null) return itf;
		return c.getSimpleName();
	}

	public static String findMontoyaInterface(
		Class<?> c,
		HashSet<Class<?>> visited
	) {
		if (c == null || visited.contains(c)) return null;
		visited.add(c);

		if (
			c.getName().startsWith("burp.api.montoya")
		) return c.getSimpleName();

		// Check interfaces
		for (Class<?> i : c.getInterfaces()) {
			String r = findMontoyaInterface(i, visited);
			if (r != null) return r;
		}

		// Check superclasses
		return findMontoyaInterface(c.getSuperclass(), visited);
	}
}
