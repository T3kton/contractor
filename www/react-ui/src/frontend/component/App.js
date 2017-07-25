import React from 'react';
import { Layout, NavDrawer, Panel, Sidebar, Chip, FontIcon, AppBar, Navigation, Button } from 'react-toolbox';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';
import Home from './Home';
import Site from './Site';
import Foundation from './Foundation';
import Structure from './Structure';
import BluePrint from './BluePrint';
import AddressBlock from './AddressBlock';
import Job from './Job';
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
            <Link to="/sites"><Button icon="business">Sites</Button></Link>
            <Link to="/blueprints"><Button icon="import_contacts">BluePrints</Button></Link>
            <Link to="/foundations"><Button icon="storage">Foundations</Button></Link>
            <Link to="/structures"><Button icon="account_balance">Structures</Button></Link>
            <Link to="/addressblocks"><Button icon="compare_arrows">Address Blocks</Button></Link>
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
            <Route path="/site/:id" render={ ( { match } ) => ( <Site id={ match.params.id } detailGet={ this.contractor.getSite } /> ) } />
            <Route path="/blueprint/f/:id" render={ ( { match } ) => ( <BluePrint id={ match.params.id } detailGet={ this.contractor.getFoundationBluePrint } /> ) } />
            <Route path="/blueprint/s/:id" render={ ( { match } ) => ( <BluePrint id={ match.params.id } detailGet={ this.contractor.getStructureBluePrint } /> ) } />
            <Route path="/foundation/:id" render={ ( { match } ) => ( <Foundation id={ match.params.id } detailGet={ this.contractor.getFoundation } /> ) } />
            <Route path="/structure/:id" render={ ( { match } ) => ( <Structure id={ match.params.id } detailGet={ this.contractor.getStructure } /> ) } />
            <Route path="/addressblock/:id" render={ ( { match } ) => ( <AddressBlock id={ match.params.id } detailGet={ this.contractor.getAddressBlock } addressListGetter={ this.contractor.getAddressBlockAddresses } /> ) } />
            <Route path="/job/f/:id" render={ ( { match } ) => ( <Job id={ match.params.id } detailGet={ this.contractor.getFoundationJob } /> ) } />
            <Route path="/job/s/:id" render={ ( { match } ) => ( <Job id={ match.params.id } detailGet={ this.contractor.getStructureJob } /> ) } />
            <Route exact={true} path="/sites" render={ () => ( <Site listGet={ this.contractor.getSiteList } /> ) } />
            <Route exact={true} path="/blueprints" render={ () => ( <BluePrint listGetF={ this.contractor.getFoundationBluePrintList } listGetS={ this.contractor.getStructureBluePrintList } /> ) }/>
            <Route exact={true} path="/foundations" render={ () => ( <Foundation site={ this.state.cur_site } listGet={ this.contractor.getFoundationList } /> ) } />
            <Route exact={true} path="/structures" render={ () => ( <Structure site={ this.state.cur_site } listGet={ this.contractor.getStructureList } /> ) } />
            <Route exact={true} path="/addressblocks" render={ () => ( <AddressBlock site={ this.state.cur_site } listGet={ this.contractor.getAddressBlockList } /> ) } />
            <Route exact={true} path="/jobs" render={ () => ( <Job site={ this.state.cur_site } listGetF={ this.contractor.getFoundationJobList } listGetS={ this.contractor.getStructureJobList } /> ) }/>
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
