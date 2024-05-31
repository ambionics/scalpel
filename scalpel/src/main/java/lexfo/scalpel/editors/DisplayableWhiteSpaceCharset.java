package lexfo.scalpel.editors;

import java.nio.ByteBuffer;
import java.nio.CharBuffer;
import java.nio.charset.*;

public class DisplayableWhiteSpaceCharset extends Charset {

	private final Charset utf8;

	public DisplayableWhiteSpaceCharset() {
		super("DisplayableWhiteSpaceCharset", null);
		utf8 = StandardCharsets.UTF_8;
	}

	public boolean contains(Charset cs) {
		return cs.equals(this);
	}

	public CharsetDecoder newDecoder() {
		return new WhitspaceCharsetDecoder(this, utf8.newDecoder());
	}

	public CharsetEncoder newEncoder() {
		return utf8.newEncoder();
	}
}

class WhitspaceCharsetDecoder extends CharsetDecoder {

	private final CharsetDecoder originalDecoder;

	protected WhitspaceCharsetDecoder(
		Charset cs,
		CharsetDecoder originalDecoder
	) {
		super(
			cs,
			originalDecoder.averageCharsPerByte(),
			originalDecoder.maxCharsPerByte()
		);
		this.originalDecoder = originalDecoder;
	}

	@Override
	protected CoderResult decodeLoop(ByteBuffer in, CharBuffer out) {
		CoderResult result = originalDecoder.decode(in, out, true);
		if (result.isUnderflow()) {
			out.flip();
			CharBuffer newBuffer = CharBuffer.allocate(out.remaining());
			while (out.hasRemaining()) {
				char c = out.get();
				if (c == '\t') {
					newBuffer.put(Character.toChars(187)[0]);
				} else if (c == '\r') {
					newBuffer.put(Character.toChars(164)[0]);
				} else if (c == '\n') {
					newBuffer.put(Character.toChars(182)[0]);
				} else if (c == Character.toChars(127)[0]) {
					newBuffer.put(Character.toChars(176)[0]);
				} else {
					newBuffer.put(c);
				}
			}
			out.clear();
			newBuffer.flip();
			out.put(newBuffer);
		}
		return result;
	}
}

class WhitspaceCharsetEncoder extends CharsetEncoder {

	private final CharsetEncoder originalEncoder;

	protected WhitspaceCharsetEncoder(
		Charset cs,
		CharsetEncoder originalEncoder
	) {
		super(
			cs,
			originalEncoder.averageBytesPerChar(),
			originalEncoder.maxBytesPerChar()
		);
		this.originalEncoder = originalEncoder;
	}

	@Override
	protected CoderResult encodeLoop(CharBuffer in, ByteBuffer out) {
		while (in.hasRemaining()) {
			char c = in.get();
			char newChar;
			if (c == '\t') {
				newChar = Character.toChars(187)[0];
			} else if (c == '\r') {
				newChar = Character.toChars(164)[0];
			} else if (c == '\n') {
				newChar = Character.toChars(182)[0];
			} else if (c == Character.toChars(127)[0]) {
				newChar = Character.toChars(176)[0];
			} else {
				newChar = c;
			}

			CoderResult result = originalEncoder.encode(
				CharBuffer.wrap(new char[] { newChar }),
				out,
				true
			);
			if (result.isOverflow()) {
				return result;
			}
		}
		return CoderResult.UNDERFLOW;
	}
}
