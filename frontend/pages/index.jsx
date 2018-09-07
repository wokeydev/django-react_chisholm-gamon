/*
import { Endpoints, GetData } from "../lib/backend";
import Page from "../layouts/Main";
import "isomorphic-unfetch";

const Index = props => (
  <Page>
    {console.log(props)}
    <h1>Homepage!</h1>
  </Page>
);

Index.getInitialProps = async function (ctx) {
  const homepageData = await GetData(Endpoints.Home);
  let homePage;
  console.log(homepageData);
  if (homepageData.items.length == 1) {
    homePage = homepageData.items[0];
  }
  return { homePage };
};

export default Index;
*/
import Page from "../layouts/Main";
const Index = props => (
  <Page>
  </Page>
);
export default Index;