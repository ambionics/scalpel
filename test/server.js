const express = require("express");

const { urlencoded } = express;

const app = express();

const bodyParser = require("body-parser");

const getRawBody = require("raw-body");

app.use(urlencoded({ extended: true }));

app.use(async (req, _res, next) => {
	req.rawBody = getRawBody(req);

	next();
});

// Known issue: duplicate headers are not supported
jsonifyRequest = (req) => ({
	url: req.url,
	url_decoded: decodeURIComponent(req.url),
	headers: (() => {
		let key;
		return Object.assign(
			{},
			...req.rawHeaders
				.map((val, i) => (i & 1 ? { [key]: val } : (key = val) && null))
				.filter((e) => e),
		);
	})(),
	body: req.body.entries && req.body.toString(),
});

app.all("/base64", (req, res) => {
	console.log("Received /base64");
	// Remove date header to ensure identical requests returns the exact same response
	res.setHeader("Date", "[REDACTED]");
	const decoded = new Buffer(req.body.toString("utf-8"), "base64").toString(
		"utf-8",
	);

	res.send(
		Buffer.from(`Received in base64:\n-----\n${decoded}\n-----`).toString(
			"base64",
		),
	);
});

app.all("/json", (req, res) => {
	console.log("Received");
	// Remove date header to ensure identical requests returns the exact same response
	// res.setHeader("Date", "[REDACTED]");
	const date = Date.now();
	console.log("Date: " + date);
	res.setHeader("Date", date);
	res.send(jsonifyRequest(req));
});

app.all("/echo", async (req, res) => {
	console.log("Received");
	// Remove date header to ensure identical requests returns the exact same response
	res.setHeader("Date", "[REDACTED]");
	res.write("HEADERS:\n");
	rawHeader = req.rawHeaders;
	for (let i = 0; i < rawHeader.length; i += 2) {
		res.write(`${rawHeader[i]}: ${rawHeader[i + 1]}\n`);
	}
	res.write("\nBODY:\n");
	res.write(await req.rawBody);
	res.end();
});

// Display a multipart form to upload multiple files
app.get("/upload", (req, res) => {
	res.send(`
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file1" />
        <input type="file" name="file2" />
        <input type="submit" value="Upload" />
    </form>
    `);
});

// Handle a multipart form
app.post("/upload", (req, res) => {
	console.log("Received");
	// Remove date header to ensure identical requests returns the exact same response
	res.setHeader("Date", "[REDACTED]");
	res.send(req.body);
});

const crypto = require("crypto");
const exp = require("constants");

const derive = (secret) => {
	const hasher = crypto.createHash("sha256");
	hasher.update(secret);
	const derived_aes_key = hasher.digest().slice(0, 32);
	return derived_aes_key;
};

const get_cipher_decrypt = (secret, iv = Buffer.alloc(16, 0)) => {
	const derived_aes_key = derive(secret);
	const cipher = crypto.createDecipheriv("aes-256-cbc", derived_aes_key, iv);
	return cipher;
};

const get_cipher_encrypt = (secret, iv = Buffer.alloc(16, 0)) => {
	const derived_aes_key = derive(secret);
	const cipher = crypto.createCipheriv("aes-256-cbc", derived_aes_key, iv);
	return cipher;
};

const decrypt = (secret, data) => {
	const decipher = get_cipher_decrypt(secret);
	let decrypted = decipher.update(data, "base64", "utf8");
	decrypted += decipher.final("utf8");
	return decrypted;
};

const encrypt = (secret, data) => {
	const cipher = get_cipher_encrypt(secret);
	let encrypted = cipher.update(data, "utf8", "base64");
	encrypted += cipher.final("base64");
	return encrypted;
};

app.post("/encrypt", (req, res) => {
	console.log(req.body);
	console.log("Received");
	res.setHeader("Date", "[REDACTED]");

	const secret = req.body["secret"];
	const data = req.body["encrypted"];

	if (data === undefined) {
		res.send("No content");
		return;
	}

	const decrypted = decrypt(secret, data);
	console.log({ decrypted });
	const resContent = `You have sent "${decrypted}" using secret "${secret}"`;
	const encrypted = encrypt(secret, resContent);

	res.send(encrypted);
});

const session = "r4nd0mh3xs7r1ng";

app.get("/encrypt-session", (req, res) => {
	res.send(session);
});

app.post("/encrypt-session", (req, res) => {
	console.log(req.body);
	console.log("Received");
	res.setHeader("Date", "[REDACTED]");

	const secret = session;
	const data = req.body["encrypted"];

	if (data === undefined) {
		res.send("No content");
		return;
	}

	const decrypted = decrypt(secret, data);
	console.log({ decrypted });
	const resContent = `You have sent "${decrypted}" using secret "${secret}"`;
	const encrypted = encrypt(secret, resContent);

	res.send(encrypted);
});

app.listen(3000, ["localhost", "nol-thinkpad"]);
