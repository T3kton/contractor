import React from 'react';
import { Layout, NavDrawer, Panel, Sidebar, Chip, FontIcon, AppBar, Navigation, Button } from 'react-toolbox';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';
import Home from './Home';
import Site from './Site';
import Foundation from './Foundation';
import Structure from './Structure';
import Complex from './Complex';
import BluePrint from './BluePrint';
import AddressBlock from './AddressBlock';
import Job from './Job';
import Todo from './Todo';
import SiteSelector from './SiteSelector';
import ServerError from './ServerError';
import Contractor from './Contractor';

class App extends React.Component
{
  state = {
    cur_site: null,
    leftDrawerVisable: true,
    autoUpdate: false,
    curJobs: 0,
    alerts: 0
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
  };

  selectSite = ( site ) =>
  {
    this.setState( { cur_site: site }, () => { this.doUpdate(); } );
  };

  serverError = ( msg, trace ) =>
  {
    this.refs.serverError.show( msg, trace );
  };

  doUpdate = () =>
  {
    if ( this.state.cur_site === undefined )
    {
      return;
    }

    this.contractor.getJobStats( this.state.cur_site )
      .then( ( result ) =>
      {
       this.setState( { curJobs: result.data.running, alerts: result.data.error } );
      } );
  };

  toggleAutoUpdate = () =>
  {
    var state = !this.state.autoUpdate;
    if( state )
    {
      this.timerID = setInterval( () => this.doUpdate(), 10000 );
    }
    else
    {
      clearInterval( this.timerID );
    }
    this.setState( { autoUpdate: state } );
  };

  componentDidMount()
  {
    this.setState( { autoUpdate: false } );
    clearInterval( this.timerID );
  }

  componentWillUnmount()
  {
    clearInterval( this.timerID );
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
          <Navigation type="vertical">
            <Link to="/"><Button icon="home">Home</Button></Link>
            <Link to="/sites"><Button icon="business">Sites</Button></Link>
            <Link to="/blueprints"><Button icon="import_contacts">BluePrints</Button></Link>
            <Link to="/foundations"><Button icon="storage">Foundations</Button></Link>
            <Link to="/structures"><Button icon="account_balance">Structures</Button></Link>
            <Link to="/complexes"><Button icon="location_city">Complexes</Button></Link>
            <Link to="/addressblocks"><Button icon="compare_arrows">Address Blocks</Button></Link>
            <Link to="/jobs"><Button icon="dvr">Jobs</Button></Link>
            <Link to="/todo"><Button icon="check_box">Todo</Button></Link>
          </Navigation>
        </NavDrawer>
        <Panel>
          <AppBar title="Contractor" leftIcon="menu" rightIcon="face" onLeftIconClick={ this.menuClick }>
            <Chip><SiteSelector onSiteChange={ this.selectSite } curSite={ this.state.cur_site } siteListGetter={ this.contractor.getSiteList } /></Chip>
            <Chip><FontIcon title='Jobs' value='dvr' /> { this.state.curJobs }</Chip>
            <Chip><FontIcon title='Alerts' value='announcement' /> { this.state.alerts }</Chip>
            <Button icon='update' inverse={ !this.state.autoUpdate } onClick={ this.toggleAutoUpdate }/>
            <Button icon='sync' inverse onClick={ this.doUpdate } />
            <Chip><Button icon='settings' disabled /></Chip>
          </AppBar>
          <div ref="content">
            <Route exact={true} path="/" component={ Home }/>
            <Route path="/site/:id" render={ ( { match } ) => ( <Site id={ match.params.id } detailGet={ this.contractor.getSite } getConfig={ this.contractor.getConfig } /> ) } />
            <Route path="/blueprint/f/:id" render={ ( { match } ) => ( <BluePrint id={ match.params.id } detailGet={ this.contractor.getFoundationBluePrint } getConfig={ this.contractor.getConfig } /> ) } />
            <Route path="/blueprint/s/:id" render={ ( { match } ) => ( <BluePrint id={ match.params.id } detailGet={ this.contractor.getStructureBluePrint } getConfig={ this.contractor.getConfig } /> ) } />
            <Route path="/foundation/:id" render={ ( { match } ) => ( <Foundation id={ match.params.id } detailGet={ this.contractor.getFoundation } detailGetDependancies={ this.contractor.getFoundationDependandyList } getConfig={ this.contractor.getConfig } /> ) } />
            <Route path="/structure/:id" render={ ( { match } ) => ( <Structure id={ match.params.id } detailGet={ this.contractor.getStructure } getConfig={ this.contractor.getConfig } /> ) } />
            <Route path="/complex/:id" render={ ( { match } ) => ( <Complex id={ match.params.id } detailGet={ this.contractor.getComplex } getConfig={ this.contractor.getConfig } /> ) } />
            <Route path="/addressblock/:id" render={ ( { match } ) => ( <AddressBlock id={ match.params.id } detailGet={ this.contractor.getAddressBlock } addressListGetter={ this.contractor.getAddressBlockAddresses } /> ) } />
            <Route path="/job/f/:id" render={ ( { match } ) => ( <Job id={ match.params.id } jobType="foundation" contractor={ this.contractor } /> ) } />
            <Route path="/job/s/:id" render={ ( { match } ) => ( <Job id={ match.params.id } jobType="structure" contractor={ this.contractor } /> ) } />
            <Route exact={true} path="/sites" render={ () => ( <Site listGet={ this.contractor.getSiteList } /> ) } />
            <Route exact={true} path="/blueprints" render={ () => ( <BluePrint listGetF={ this.contractor.getFoundationBluePrintList } listGetS={ this.contractor.getStructureBluePrintList } /> ) }/>
            <Route exact={true} path="/foundations" render={ () => ( <Foundation site={ this.state.cur_site } listGet={ this.contractor.getFoundationList } /> ) } />
            <Route exact={true} path="/structures" render={ () => ( <Structure site={ this.state.cur_site } listGet={ this.contractor.getStructureList } /> ) } />
            <Route exact={true} path="/complexes" render={ () => ( <Complex site={ this.state.cur_site } listGet={ this.contractor.getComplexList } /> ) } />
            <Route exact={true} path="/addressblocks" render={ () => ( <AddressBlock site={ this.state.cur_site } listGet={ this.contractor.getAddressBlockList } /> ) } />
            <Route exact={true} path="/jobs" render={ () => ( <Job site={ this.state.cur_site } listGetF={ this.contractor.getFoundationJobList } listGetS={ this.contractor.getStructureJobList } /> ) }/>
            <Route exact={true} path="/todo" render={ () => ( <Todo site={ this.state.cur_site } listGet={ this.contractor.getTodoList } classListGet={ this.contractor.getFoundationClassList } /> ) }/>
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
