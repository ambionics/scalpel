package lexfo.scalpel.editors;

import burp.api.montoya.core.ByteArray;
import burp.api.montoya.http.HttpService;
import burp.api.montoya.http.message.HttpMessage;
import burp.api.montoya.http.message.HttpRequestResponse;
import burp.api.montoya.ui.editor.extension.EditorCreationContext;
import burp.api.montoya.ui.editor.extension.ExtensionProvidedHttpRequestEditor;
import burp.api.montoya.ui.editor.extension.ExtensionProvidedHttpResponseEditor;
import lexfo.scalpel.EditorType;
import lexfo.scalpel.Result;

/**
 * Interface declaring all the necessary methods to implement a Scalpel editor
 * If you wish to implement your own type of editor, you should use the AbstractEditor class as a base.
 */
public interface IMessageEditor
	extends
		ExtensionProvidedHttpRequestEditor,
		ExtensionProvidedHttpResponseEditor {
	HttpRequestResponse getRequestResponse();

	boolean setRequestResponseInternal(HttpRequestResponse requestResponse);

	HttpService getHttpService();

	Result<ByteArray, Throwable> executeHook(HttpRequestResponse reqRes)
		throws Throwable;

	boolean updateContent(HttpRequestResponse reqRes);

	EditorType getEditorType();

	String getId();

	EditorCreationContext getCtx();

	HttpMessage getMessage();

	HttpMessage processOutboundMessage();
}
