// API Connection library to backend
import "isomorphic-unfetch";

const APIRoot = "http://localhost:8000";
const APIPages = APIRoot + "/api/cms/pages/";

export const Endpoints = {
  Pages: APIPages,
  Home: APIPages + "?fields=*&type=chisholm.HomePage&slug=home",
  Catchall: APIPages + "find/?fields=*&html_path="
};

function _objToQueryString(obj) {
  // Turns a data array (key/value) into Querystring
  const keyValuePairs = [];
  for (const key in obj) {
    keyValuePairs.push(
      encodeURIComponent(key) + "=" + encodeURIComponent(obj[key])
    );
  }
  return keyValuePairs.join("&");
}

export async function GetData(endpoint, data, headers = {}) {
  // Connects to an API endpoint and returns the data
  let fullEndpoint = endpoint;
  console.log(fullEndpoint);
  if (data) {
    fullEndpoint += "?" + _objToQueryString(data);
  }
  const res = await fetch(fullEndpoint, {
    method: "get",
    headers: headers
  });
  if (res.ok === true) {
    const ret = await res.json();
    return ret;
  }
}
