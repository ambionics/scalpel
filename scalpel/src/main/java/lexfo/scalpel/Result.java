package lexfo.scalpel;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;

/**
 * Optional-style class for handling python task results
 *
 * A completed python task can have multiple outcomes:
 * 	- The task completes successfully and returns a value
 * 	- The task completes successfully but returns no value
 *  - The task throws an exception
 *
 * Result allows us to handle returned values and errors uniformly to handle them when needed.
 */
public class Result<T, E extends Throwable> {

	private final T value;
	private final E error;
	private final boolean isEmpty;

	private Result(T value, E error, boolean isEmpty) {
		this.value = value;
		this.error = error;
		this.isEmpty = isEmpty;
	}

	public static <T, E extends Throwable> Result<T, E> success(T value) {
		return new Result<>(value, null, false);
	}

	public static <T, E extends Throwable> Result<T, E> empty() {
		return new Result<>(null, null, true);
	}

	public static <T, E extends Throwable> Result<T, E> error(E error) {
		return new Result<>(null, error, false);
	}

	public boolean isSuccess() {
		return error == null;
	}

	public boolean hasValue() {
		return isSuccess() && !isEmpty();
	}

	public T getValue() {
		if (!isSuccess()) {
			throw new RuntimeException("Result is in error state", error);
		}
		if (isEmpty) {
			throw new IllegalStateException("Result is empty");
		}
		return value;
	}

	public E getError() {
		return error;
	}

	public boolean isEmpty() {
		return isEmpty && isSuccess();
	}

	@Override
	public String toString() {
		if (isSuccess()) {
			if (isEmpty) {
				return "<empty>";
			} else {
				return String.valueOf(value);
			}
		} else {
			// Convert stacktrace to string
			final StringWriter sw = new StringWriter();
			final PrintWriter pw = new PrintWriter(sw);
			error.printStackTrace(pw);
			return sw.toString();
		}
	}

	public <U> Result<U, E> map(Function<? super T, ? extends U> mapper) {
		if (isSuccess() && !isEmpty) {
			return new Result<>(mapper.apply(value), null, false);
		} else if (isEmpty) {
			return empty();
		} else {
			return error(error);
		}
	}

	public <U> Result<U, E> flatMap(Function<? super T, Result<U, E>> mapper) {
		if (isSuccess() && !isEmpty) {
			return mapper.apply(value);
		} else if (isEmpty) {
			return empty();
		} else {
			return error(error);
		}
	}

	public Result<T, E> or(Result<T, E> other) {
		return isSuccess() ? this : other;
	}

	public T orElse(T other) {
		return isSuccess() && !isEmpty ? value : other;
	}

	public T orElseGet(Supplier<? extends T> other) {
		return isSuccess() && !isEmpty ? value : other.get();
	}

	public void ifSuccess(Consumer<T> action) {
		if (isSuccess() && !isEmpty) {
			action.accept(value);
		}
	}

	public void ifError(Consumer<E> action) {
		if (!isSuccess()) {
			action.accept(error);
		}
	}

	public void ifEmpty(Runnable action) {
		if (isEmpty) {
			action.run();
		}
	}
}
