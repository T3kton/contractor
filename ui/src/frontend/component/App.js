import React from 'react';
import { Layout, NavDrawer, Panel, Sidebar, Chip, FontIcon, AppBar, Navigation, Button, Dialog, Input } from 'react-toolbox';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';
import Home from './Home';
import Site from './Site';
import Plot from './Plot';
import Network from './Network';
import Foundation from './Foundation';
import Dependency from './Dependency';
import Structure from './Structure';
import Complex from './Complex';
import BluePrint from './BluePrint';
import PXE from './PXE';
import AddressBlock from './AddressBlock';
import Job from './Job';
import Cartographer from './Cartographer';
import JobLog from './JobLog';
import Todo from './Todo';
import SiteGraph from './SiteGraph';
import SiteSelector from './SiteSelector';
import ServerError from './ServerError';
import Contractor from './Contractor';

class App extends React.Component
{
  state = {
    cur_site: null,
    loginVisible: false,
    username: '',
    password: '',
    leftDrawerVisable: true,
    autoUpdate: false,
    curJobs: 0,
    alerts: 0
  };

  constructor( props )
  {
    super( props );
    this.contractor = new Contractor( window.API_BASE_URI );
    this.contractor.cinp.server_error_handler = this.serverError;
  }

  handleChange = ( name, value ) => {
    this.setState({...this.state, [name]: value});
  };

  menuClick = () =>
  {
    this.setState( { leftDrawerVisable: !this.state.leftDrawerVisable } );
  };

  showLogin = () =>
  {
    this.setState( { loginVisible: true } );
  };

  closeLogin = () =>
  {
    this.setState( { loginVisible: false } );
  };

  doLogin = () =>
  {
    this.contractor.login( this.state.username, this.state.password )
      .then( ( result ) =>
        {
          this.contractor.setAuth( this.state.username, result.data );
          this.setState( { loginVisible: false } );
          this.handleChange( 'password', '' );
        },
        ( result ) =>
        {
          alert( 'Error logging in: "' + result.detail + '"' );
        } );
    this.setState( { 'password': '' } );
  }

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

    if( !this.contractor.authenticated )
    {
      return;
    }

    this.contractor.getJobStats( this.state.cur_site )
      .then( ( result ) =>
        {
          this.setState( { curJobs: result.data.running, alerts: result.data.error } );
        }
     );
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

  loginActions = [
    { label: "Close", onClick: this.closeLogin },
    { label: "Login", onClick: this.doLogin },
  ];

  render()
  {
    return (
<Router>
  <div>
    <ServerError ref="serverError" />
    <div>
      <Dialog
        actions={ this.loginActions }
        active={ this.state.loginVisible }
        onEscKeyDown={ this.closeLogin }
        onOverlayClick={ this.closeLogin }
        title='Login'
      >
        <div>
          <Input type='text' label='Username' name='username' value={ this.state.username } onChange={this.handleChange.bind( this, 'username' ) } />
          <Input type='password' label='Password' name='password' value={ this.state.password } onChange={this.handleChange.bind( this, 'password' ) } />
        </div>
      </Dialog>
      <Layout>
        <NavDrawer pinned={ this.state.leftDrawerVisable }>
          <Navigation type="vertical">
            <Link to="/"><Button icon="home">Home</Button></Link>
            <Link to="/sites"><Button icon="business">Sites</Button></Link>
            <Link to="/plots"><Button icon="map">Plots</Button></Link>
            <Link to="/networks"><Button icon="router">Networks</Button></Link>
            <Link to="/blueprints"><Button icon="import_contacts">BluePrints</Button></Link>
            <Link to="/pxes"><Button icon="import_contacts">PXEs</Button></Link>
            <Link to="/foundations"><Button icon="storage">Foundations</Button></Link>
            <Link to="/dependancies"><Button icon="group_work">Dependancies</Button></Link>
            <Link to="/structures"><Button icon="account_balance">Structures</Button></Link>
            <Link to="/complexes"><Button icon="location_city">Complexes</Button></Link>
            <Link to="/addressblocks"><Button icon="compare_arrows">Address Blocks</Button></Link>
            <Link to="/jobs"><Button icon="dvr">Jobs</Button></Link>
            <Link to="/cartographer"><Button icon="public">Cartographer</Button></Link>
            <Link to="/joblog"><Button icon="reorder">Job Log</Button></Link>
            <Link to="/todo"><Button icon="check_box">Todo</Button></Link>
            <Link to="/graph"><Button icon="timeline">Graph</Button></Link>
          </Navigation>
        </NavDrawer>
        <Panel>
          <AppBar title="Contractor" leftIcon="menu" rightIcon="face" onLeftIconClick={ this.menuClick } onRightIconClick={ this.showLogin }>
            <SiteSelector onSiteChange={ this.selectSite } curSite={ this.state.cur_site } contractor={ this.contractor } />
            <Chip><FontIcon title='Jobs' value='dvr' /> { this.state.curJobs }</Chip>
            <Chip><FontIcon title='Alerts' value='announcement' /> { this.state.alerts }</Chip>
            <Button icon='update' inverse={ !this.state.autoUpdate } onClick={ this.toggleAutoUpdate } />
            <Button icon='sync' inverse onClick={ this.doUpdate } />
          </AppBar>
          <div ref="content">
            <Route exact={true} path="/" component={ Home }/>
            <Route path="/site/:id" render={ ( { match } ) => ( <Site id={ match.params.id } contractor={ this.contractor } detailGet={ this.contractor.getSite } getConfig={ this.contractor.getConfig } /> ) } />
            <Route path="/plot/:id" render={ ( { match } ) => ( <Plot id={ match.params.id } detailGet={ this.contractor.getPlot } /> ) } />
            <Route path="/blueprint/f/:id" render={ ( { match } ) => ( <BluePrint id={ match.params.id } detailGet={ this.contractor.getFoundationBluePrint } getConfig={ this.contractor.getConfig } getScript={ this.contractor.getScript }/> ) } />
            <Route path="/network/:id" render={ ( { match } ) => ( <Network id={ match.params.id } detailGet={ this.contractor.getNetwork } /> ) } />
            <Route path="/blueprint/s/:id" render={ ( { match } ) => ( <BluePrint id={ match.params.id } detailGet={ this.contractor.getStructureBluePrint } getConfig={ this.contractor.getConfig } getScript={ this.contractor.getScript } /> ) } />
            <Route path="/pxe/:id" render={ ( { match } ) => ( <PXE id={ match.params.id } detailGet={ this.contractor.getPXE } /> ) } />
            <Route path="/foundation/:id" render={ ( { match } ) => ( <Foundation id={ match.params.id } detailGet={ this.contractor.getFoundation } getFoundationInterfaces={ this.contractor.getFoundationInterfaces } detailGetDependancies={ this.contractor.getFoundationDependandyList } getConfig={ this.contractor.getConfig } /> ) } />
            <Route path="/dependency/:id" render={ ( { match } ) => ( <Dependency id={ match.params.id } detailGet={ this.contractor.getDependency } /> ) } />
            <Route path="/structure/:id" render={ ( { match } ) => ( <Structure id={ match.params.id } detailGet={ this.contractor.getStructure } getConfig={ this.contractor.getConfig } getAddressList={ this.contractor.getStructureAddressList } /> ) } />
            <Route path="/complex/:id" render={ ( { match } ) => ( <Complex id={ match.params.id } detailGet={ this.contractor.getComplex } getConfig={ this.contractor.getConfig } /> ) } />
            <Route path="/addressblock/:id" render={ ( { match } ) => ( <AddressBlock id={ match.params.id } detailGet={ this.contractor.getAddressBlock } addressListGetter={ this.contractor.getAddressBlockAddresses } /> ) } />
            <Route path="/job/f/:id" render={ ( { match } ) => ( <Job id={ match.params.id } jobType="foundation" contractor={ this.contractor } /> ) } />
            <Route path="/job/s/:id" render={ ( { match } ) => ( <Job id={ match.params.id } jobType="structure" contractor={ this.contractor } /> ) } />
            <Route path="/job/d/:id" render={ ( { match } ) => ( <Job id={ match.params.id } jobType="dependency" contractor={ this.contractor } /> ) } />
            <Route exact={true} path="/sites" render={ () => ( <Site contractor={ this.contractor } /> ) } />
            <Route exact={true} path="/plots" render={ () => ( <Plot listGet={ this.contractor.getPlotList } /> ) } />
            <Route exact={true} path="/networks" render={ () => ( <Network site={ this.state.cur_site } listGet={ this.contractor.getNetworkList } /> ) } />
            <Route exact={true} path="/blueprints" render={ () => ( <BluePrint listGetF={ this.contractor.getFoundationBluePrintList } listGetS={ this.contractor.getStructureBluePrintList } /> ) }/>
            <Route exact={true} path="/pxes" render={ () => ( <PXE site={ this.state.cur_site } listGet={ this.contractor.getPXEList } /> ) } />
            <Route exact={true} path="/foundations" render={ () => ( <Foundation site={ this.state.cur_site } listGet={ this.contractor.getFoundationList } /> ) } />
            <Route exact={true} path="/dependancies" render={ () => ( <Dependency site={ this.state.cur_site } listGet={ this.contractor.getDependencyList } /> ) } />
            <Route exact={true} path="/structures" render={ () => ( <Structure site={ this.state.cur_site } listGet={ this.contractor.getStructureList } /> ) } />
            <Route exact={true} path="/complexes" render={ () => ( <Complex site={ this.state.cur_site } listGet={ this.contractor.getComplexList } /> ) } />
            <Route exact={true} path="/addressblocks" render={ () => ( <AddressBlock site={ this.state.cur_site } listGet={ this.contractor.getAddressBlockList } /> ) } />
            <Route exact={true} path="/jobs" render={ () => ( <Job site={ this.state.cur_site } listGetF={ this.contractor.getFoundationJobList } listGetS={ this.contractor.getStructureJobList } listGetD={ this.contractor.getDependencyJobList } /> ) } />
            <Route exact={true} path="/cartographer" render={ () => ( <Cartographer listGet={ this.contractor.getCartographerList } /> ) } />
            <Route exact={true} path="/joblog" render={ () => ( <JobLog site={ this.state.cur_site } listGet={ this.contractor.getJobLogList } /> ) } />
            <Route exact={true} path="/todo" render={ () => ( <Todo site={ this.state.cur_site } listGet={ this.contractor.getTodoList } classListGet={ this.contractor.getFoundationClassList } /> ) } />
            <Route exact={true} path="/graph" render={ () => ( <SiteGraph site={ this.state.cur_site } siteDependencyMap={ this.contractor.getSiteDependencyMap } /> ) } />
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
