import { Endpoints, GetData } from "../lib/backend";
import Page from "../layouts/Main";
import "isomorphic-unfetch";

const ContentPage = props => (
    <Page>
        {console.log(props)}
        <h1>General content page</h1>
    </Page>
);

ContentPage.getInitialProps = async function (ctx) {
    const endpont = Endpoints.Catchall + ctx.query.slug
    const pageData = await GetData(endpont);
    return { pageData };
};

export default ContentPage;
