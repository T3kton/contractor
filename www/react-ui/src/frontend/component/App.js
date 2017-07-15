import React from 'react';
import ServerError from './ServerError';
import NavFrame from './NavFrame';
import Contractor from './Contractor';

class App extends React.Component
{
  constructor()
  {
    super();
    this.cur_site = null;
    this.contractor = new Contractor( 'http://127.0.0.1:8888/' );
    this.contractor.cinp.server_error_handler = this.serverError;
  }

  selectSite = ( site ) =>
  {
    this.cur_site = site;
    alert( "new Site: '" + site + "'" );
  }

  connect = () =>
  {
    this.contractor.cinp.get( '/api/v1/Site:site1:' ).then(
      ( value, multi, uri ) => { alert( value ); },
      ( err_msg ) => { console.error( 'Error getting "' + err_msg + '"'); } );
    //alert( contractor.getSiteList() );
  }

  serverError = ( msg, trace ) =>
  {
    this.refs.serverError.show( msg, trace );
  }

  render()
  {
    return (
  <div>
    <ServerError ref="serverError" />
    <NavFrame onSiteChange={this.selectSite} onConnect={this.connect} />
    <div id="content" />
  </div>
);
  }

}

export default App;
