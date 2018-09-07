import { Endpoints, GetData } from "../../lib/backend";
import Page from "../../layouts/Main";
import "isomorphic-unfetch";

const Index = props => (
  <Page>
    {console.log(props)}
    <h1>Search Page</h1>
  </Page>
);

export default Index;
