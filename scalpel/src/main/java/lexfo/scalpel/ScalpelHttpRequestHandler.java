/*
 * Copyright (c) 2023. PortSwigger Ltd. All rights reserved.
 *
 * This code may be used to extend the functionality of Burp Suite Community Edition
 * and Burp Suite Professional, provided that this usage does not violate the
 * license terms for those products.
 */

package lexfo.scalpel;

import burp.api.montoya.MontoyaApi;
import burp.api.montoya.http.HttpService;
import burp.api.montoya.http.handler.*;
import burp.api.montoya.http.message.requests.HttpRequest;
import java.util.Optional;
import lexfo.scalpel.components.ErrorPopup;

/**
  Handles HTTP requests and responses.
*/
public class ScalpelHttpRequestHandler implements HttpHandler {

	private final MontoyaApi API;
	private final ErrorPopup popup;
	/**
    	The ScalpelExecutor object used to execute Python scripts.
  	*/
	private final ScalpelExecutor executor;

	/**
		Constructs a new ScalpelHttpRequestHandler object with the specified MontoyaApi object and ScalpelExecutor object.
		@param API The MontoyaApi object to use.
		@param editorProvider The ScalpelEditorProvider object to use.
		@param executor The ScalpelExecutor object to use.
  	*/
	public ScalpelHttpRequestHandler(
		MontoyaApi API,
		ScalpelEditorProvider editorProvider,
		ScalpelExecutor executor
	) {
		// Reference the executor to be able to call Python callbacks.
		this.executor = executor;
		this.API = API;
		this.popup = new ErrorPopup(API);
	}

	/**
		Handles HTTP requests.
		@param httpRequestToBeSent The HttpRequestToBeSent object containing information about the HTTP request.
		@return A RequestToBeSentAction object containing information about how to handle the HTTP request.
	*/
	@Override
	public RequestToBeSentAction handleHttpRequestToBeSent(
		HttpRequestToBeSent httpRequestToBeSent
	) {
		// Call the request() Python callback
		final Result<HttpRequest, Throwable> newReq = executor.callIntercepterHook(
			httpRequestToBeSent,
			httpRequestToBeSent.httpService()
		);

		newReq.ifError(e -> {
			final String title =
				"Error in request() hook (" +
				httpRequestToBeSent.toolSource().toolType().toolName() +
				"): " +
				httpRequestToBeSent.url();
			ConfigTab.putStringToOutput(
				ScalpelLogger.exceptionToErrorMsg(e, title),
				false
			);

			if (
				Config.getInstance().getDisplayProxyErrorPopup().equals("True")
			) {
				final String errorMsg = ScalpelLogger.exceptionToErrorMsg(
					e,
					title
				);
				popup.addError(errorMsg);
			}
		});

		// Return the modified request when requested, else return the original.
		return RequestToBeSentAction.continueWith(
			newReq.orElse(httpRequestToBeSent)
		);
	}

	/**
		Handles HTTP responses.
		@param httpResponseReceived The HttpResponseReceived object containing information about the HTTP response.
		@return A ResponseReceivedAction object containing information about how to handle the HTTP response.
  	*/
	@Override
	public ResponseReceivedAction handleHttpResponseReceived(
		HttpResponseReceived httpResponseReceived
	) {
		// Get the network info form the initiating request.
		final HttpService service = Optional
			.ofNullable(httpResponseReceived.initiatingRequest())
			.map(HttpRequest::httpService)
			.orElse(null);

		// Call the request() Python callback
		final Result<HttpResponseReceived, Throwable> newRes = executor.callIntercepterHook(
			httpResponseReceived,
			service
		);

		newRes.ifError(e -> {
			final String title =
				"Error in response() hook (" +
				httpResponseReceived.toolSource().toolType().toolName() +
				"):  " +
				httpResponseReceived.initiatingRequest().url();
			ConfigTab.putStringToOutput(
				ScalpelLogger.exceptionToErrorMsg(e, title),
				false
			);

			if (
				Config.getInstance().getDisplayProxyErrorPopup().equals("True")
			) {
				final String errorMsg = ScalpelLogger.exceptionToErrorMsg(
					e,
					title
				);
				popup.addError(errorMsg);
			}
		});

		// Return the modified request when requested, else return the original.
		return ResponseReceivedAction.continueWith(
			newRes.orElse(httpResponseReceived)
		);
	}
}
