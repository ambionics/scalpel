package lexfo.scalpel;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.concurrent.ExecutionException;
import java.util.function.Consumer;
import java.util.function.Supplier;

public class IO {

	private static final ObjectMapper mapper = new ObjectMapper();

	@FunctionalInterface
	public interface IOSupplier<T> {
		T call() throws IOException, InterruptedException, ExecutionException;
	}

	@FunctionalInterface
	public interface IORunnable {
		void run() throws IOException, InterruptedException, ExecutionException;
	}

	public static <T> T ioWrap(IOSupplier<T> supplier) {
		try {
			return supplier.call();
		} catch (IOException | InterruptedException | ExecutionException e) {
			throw new RuntimeException(e);
		}
	}

	public static void run(IORunnable supplier) {
		try {
			supplier.run();
		} catch (IOException | InterruptedException | ExecutionException e) {}
	}

	public static <T> T ioWrap(
		IOSupplier<T> supplier,
		Supplier<T> defaultSupplier
	) {
		try {
			return supplier.call();
		} catch (IOException | InterruptedException | ExecutionException e) {
			return defaultSupplier.get();
		}
	}

	public static <T> T readJSON(File file, TypeReference<T> typeRef) {
		return ioWrap(() -> mapper.readValue(file, typeRef));
	}

	public static <T> T readJSON(
		File file,
		TypeReference<T> typeRef,
		Consumer<IOException> errorHandler
	) {
		return ioWrap(
			() -> mapper.readValue(file, typeRef),
			() -> {
				errorHandler.accept(new IOException());
				return null;
			}
		);
	}

	public static <T> T readJSON(File file, Class<T> clazz) {
		return ioWrap(() -> mapper.readValue(file, clazz));
	}

	public static <T> T readJSON(
		File file,
		Class<T> clazz,
		Consumer<IOException> errorHandler
	) {
		return ioWrap(
			() -> mapper.readValue(file, clazz),
			() -> {
				errorHandler.accept(new IOException());
				return null;
			}
		);
	}

	public static <T> T readJSON(String json, Class<T> clazz) {
		return ioWrap(() -> mapper.readValue(json, clazz));
	}

	public static void writeJSON(File file, Object obj) {
		ioWrap(() -> {
			mapper.writerWithDefaultPrettyPrinter().writeValue(file, obj);

			new FileWriter(file, true).append('\n').close();
			return null;
		});
	}

	public static void writeFile(String path, String content) {
		ioWrap(() -> {
			FileWriter writer = new FileWriter(path);
			writer.write(content);
			writer.close();
			return null;
		});
	}

	public static void sleep(Integer ms) {
		ioWrap(() -> {
			Thread.sleep(ms);
			return null;
		});
	}
}
