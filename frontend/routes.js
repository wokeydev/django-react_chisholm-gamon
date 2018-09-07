// Defines routes extra to those handled by the next.js
// file structure (pages/<page>.js)

const routes = require("next-routes");

module.exports = routes().add("content_page", "/:slug", "_content_page");
