package lexfo.scalpel;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class Async {

	private static final Executor executor = Executors.newFixedThreadPool(10);

	public static CompletableFuture<Void> run(Runnable runnable) {
		return CompletableFuture.runAsync(runnable, executor);
	}
}
