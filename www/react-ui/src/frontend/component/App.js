import React from 'react';
import { Layout, NavDrawer, Panel, Sidebar, Chip, FontIcon, AppBar, Navigation, Button } from 'react-toolbox';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';
import Home from './Home';
import Foundations from './Foundations';
import SiteSelector from './SiteSelector';
import ServerError from './ServerError';
import Contractor from './Contractor';

class App extends React.Component
{
  state = {
    cur_site: null,
    leftDrawerVisable: true
  };

  constructor()
  {
    super();
    this.contractor = new Contractor( 'http://127.0.0.1:8888' );
    this.contractor.cinp.server_error_handler = this.serverError;
  }

  menuClick = () =>
  {
    this.setState( { leftDrawerVisable: !this.state.leftDrawerVisable} );
  }

  selectSite = ( site ) =>
  {
    this.setState( { cur_site: site }  );
  }

  serverError = ( msg, trace ) =>
  {
    this.refs.serverError.show( msg, trace );
  }

  render()
  {
    return (
<Router>
  <div>
    <ServerError ref="serverError" />
    <div>
      <Layout>
        <NavDrawer pinned={this.state.leftDrawerVisable}>
          <Navigation type='vertical'>
            <Link to="/"><Button icon="home">Home</Button></Link>
            <Link to="/foundations"><Button icon="storage">Foundations</Button></Link>
            <Link to="/structures"><Button icon="account_balance">Structures</Button></Link>
            <Link to="/networks"><Button icon="compare_arrows">Networks</Button></Link>
            <Link to="/jobs"><Button icon="dvr">Jobs</Button></Link>
          </Navigation>
        </NavDrawer>
        <Panel>
          <AppBar title="Contractor" leftIcon="menu" rightIcon="face" onLeftIconClick={ this.menuClick }>
            <Chip><SiteSelector onSiteChange={ this.selectSite } curSite={ this.state.cur_site } siteListGetter={ this.contractor.getSiteList } /></Chip>
            <Chip><FontIcon title='Jobs' value='dvr' /> 0</Chip>
            <Chip><FontIcon value='announcement' /> 0</Chip>
            <Button icon='sync' disabled/>
            <Button icon='update' disabled />
            <Button icon='settings' disabled />
          </AppBar>
          <div>
            <Route exact={true} path="/" component={ Home }/>
            <Route path="/foundations/:id" render={ ( { match } ) => ( <Foundations uid={ match.params.id } foundationGet={ this.contractor.getFoundation } /> ) } />
            <Route exact={true} path="/foundations" render={ () => ( <Foundations site={ this.state.cur_site } foundationListGetter={ this.contractor.getFoundationList } /> ) } />
            <Route exact={true} path="/structures" render={ () => ( <h2>Structures</h2> ) }/>
            <Route exact={true} path="/networks" render={ () => ( <h2>Networks</h2> ) }/>
            <Route exact={true} path="/jobs" render={ () => ( <h2>Jobs</h2> ) }/>
          </div>
        </Panel>
      </Layout>
    </div>

  </div>
</Router>
);
  }

}

export default App;
