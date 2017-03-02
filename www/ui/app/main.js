const api_host = 'http://127.0.0.1:8888/'
const base_path = '/api/v1/'

var contractor;

$( document ).ready( function()
{
  cinp = cinpBuilder( api_host );
  cinp.server_error_handler = serverError;
  contractor = contractorBuilder( cinp );

  $( window ).on( 'hashchange', handleHashChange );
  handleHashChange();

  contractor.getSiteList().done( updateSiteList ).fail( function( message ) { alert( 'Error loading sites "' + message + '"' ); } );

} );

function updateSiteList( object_map )
{
  var foundation_dd = $( '#site-foundation-dropdown' );
  var structure_dd = $( '#site-structure-dropdown' );
  var job_dd = $( '#site-job-dropdown' );

  foundation_dd.empty();
  structure_dd.empty();
  job_dd.empty();

  for( site_id in object_map )
  {
    var site = object_map[ site_id ];
    foundation_dd.append( $( '<li>' + site.description + '</li>' ).on( 'click', setFoundationSite ).data( 'site', site_id ) );
    structure_dd.append( $( '<li>' + site.description + '</li>' ).on( 'click', setStructureSite ).data( 'site', site_id ) );
    job_dd.append( $( '<li>' + site.description + '</li>' ).on( 'click', setJobSite ).data( 'site', site_id ) );
  }
}

function setFoundationSite( event )
{
  var element = $( this );

  contractor.getFoundationList( element.data( 'site' ) ).done( updateFoundationTable ).fail( function( message ) { alert( 'Error loading foundations "' + message + '"' ); } );
}

function updateFoundationTable( object_map )
{
  var tbody = $( '#foundation-list-table tbody' );

  tbody.empty();

  for( var uri in object_map )
  {
    var entry = object_map[ uri ];
    var row = $( '<tr><td>' + uri + '</td><td>' + entry.locator + '</td><td>' + entry.type + '</td><td>' + entry.blueprint + '</td><td>' + entry.state + '</td></tr>' );
    row.find( 'td:first' ).on( 'click', function() { contractor.cinp.get( $( this ).html() ).done( showObject ); } );
    row.find( 'td:eq( 3 )' ).on( 'click', function() { contractor.cinp.get( $( this ).html() ).done( showObject ); } );
    tbody.append( row );
  }
}

function setStructureSite( event )
{
  var element = $( this );

  contractor.getStructureList( element.data( 'site' ) ).done( updateStructureTable ).fail( function( message ) { alert( 'Error loading structures "' + message + '"' ); } );
}

function updateStructureTable( object_map )
{
  var tbody = $( '#structure-list-table tbody' );

  tbody.empty();

  for( var uri in object_map )
  {
    var entry = object_map[ uri ];
    var row = $( '<tr><td>' + uri + '</td><td>' + entry.hostname + '</td><td>' + entry.blueprint + '</td><td>' + entry.state + '</td></tr>' );
    row.find( 'td:first' ).on( 'click', function() { contractor.cinp.get( $( this ).html() ).done( showObject ); } );
    row.find( 'td:eq( 2 )' ).on( 'click', function() { contractor.cinp.get( $( this ).html() ).done( showObject ); } );
    tbody.append( row );
  }
}

function setJobSite( event )
{
  var element = $( this );

  contractor.getFoundationJobList( element.data( 'site' ) ).done( updateFoundationJobTable ).fail( function( message ) { alert( 'Error loading jobs "' + message + '"' ); } );
  contractor.getStructureJobList( element.data( 'site' ) ).done( updateStructureJobTable ).fail( function( message ) { alert( 'Error loading jobs "' + message + '"' ); } );
}

function updateFoundationJobTable( object_map )
{
  var tbody = $( '#job-foundation-list-table tbody' );

  tbody.empty();

  for( var uri in object_map )
  {
    var entry = object_map[ uri ];
    var row = $( '<tr><td>' + uri.split( ':' )[1] + '</td><td>' + entry.script_name + '</td><td>' + entry.foundation + '</td><td>' + entry.message + '</td><td>' + entry.progress + '</td><td>' + entry.state + '</td><td>' + entry.status + '</td><td>' + entry.updated + '</td><td id="buttons"/></tr>' );
    row.find( 'td:first' ).on( 'click', function() { contractor.cinp.get( uri ).done( showObject ); } );
    row.find( 'td:eq( 2 )' ).on( 'click', function() { contractor.cinp.get( $( this ).html() ).done( showObject ); } );
    if( entry.state == 'paused' )
    {
      var button = $( '<button>Resume</button>' );
      button.on( 'click', function() { contractor.cinp.call( uri + '(resume)' ).done( function(){ alert( 'Job Resumed' ); updateFoundationJobTable(); } ).fail( function( message ) { alert( 'Error Resuming Job "' + message + '"' ); } ); } );
      row.find( '#buttons' ).append( button );
    }
    else if( entry.state == 'error' )
    {
      var button = $( '<button>Reset</button>' );
      button.on( 'click', function() { contractor.cinp.call( uri + '(reset)' ).done( function(){ alert( 'Job Reset' ); updateFoundationJobTable(); } ).fail( function( message ) { alert( 'Error Resetting Job "' + message + '"' ); } ); } );
      row.find( '#buttons' ).append( button );
    }
    else if( entry.state == 'queued' )
    {
      var button = $( '<button>Pause</button>' );
      button.on( 'click', function() { contractor.cinp.call( uri + '(pause)' ).done( function(){ alert( 'Job Paused' ); updateFoundationJobTable(); } ).fail( function( message ) { alert( 'Error Pausing Job "' + message + '"' ); } ); } );
      row.find( '#buttons' ).append( button );
    }
    if( entry.state != 'done' ) // actualy status.entry[ status.entry.length - 1 ][1] == 'Function'   except status.entry is just text right now
    {
      var button = $( '<button>Rollback</button>' );
      button.on( 'click', function() { contractor.cinp.call( uri + '(rollback)' ).done( function(){ alert( 'Job Rolled Back' ); updateFoundationJobTable(); } ).fail( function( message ) { alert( 'Error Rolling Back Job "' + message + '"' ); } ); } );
      row.find( '#buttons' ).append( button );
      tbody.append( row );
    }
  }
}

function updateStructureJobTable( object_map )
{
  var tbody = $( '#job-structure-list-table tbody' );

  tbody.empty();

  for( var uri in object_map )
  {
    var entry = object_map[ uri ];
    var row = $( '<tr><td>' + uri.split( ':' )[1] + '</td><td>' + entry.script_name + '</td><td>' + entry.structure + '</td><td>' + entry.message + '</td><td>' + entry.progress + '</td><td>' + entry.state + '</td><td>' + entry.status + '</td><td>' + entry.updated + '</td><td id="buttons"/></tr>' );
    row.find( 'td:first' ).on( 'click', function() { contractor.cinp.get( uri ).done( showObject ); } );
    row.find( 'td:eq( 2 )' ).on( 'click', function() { contractor.cinp.get( $( this ).html() ).done( showObject ); } );
    tbody.append( row );
  }
}

function showObject( data, multi, uri )
{
  $( '#object-detail-dialog .modal-title' ).html( 'Detail for ' + uri );
  var body = $( '#object-detail-dialog .modal-body tbody' );
  body.empty();

  for( var item of [ 'Building/Foundation', 'Building/Structure', 'Site/Site', 'BluePrint/StructureBluePrint', 'BluePrint/FoundationBluePrint' ] )
  {
    if( uri.startsWith( '/api/v1/' + item ) )
    {
      var row = $( '<tr><td colspan="2"><button>Get Full Config</button></td></tr>' );
      row.find( 'button' ).on( 'click', function() { $( '#object-detail-dialog' ).modal( 'hide' ); contractor.cinp.call( uri + '(getConfig)' ).done( show ); } );
      body.append( row );
    }
  }

  if( uri.startsWith( '/api/v1/Building/Foundation' ) )
  {
    var row = $( '<tr><td colspan="2"><button>Get Real Foundation</button></td></tr>' );
    row.find( 'button' ).on( 'click', function()
      {
        $( '#object-detail-dialog' ).modal( 'hide' );
        contractor.cinp.call( uri + '(getRealFoundationURI)' ).done( function( uri )
          {
            contractor.cinp.get( uri ).done( showObject );
          }
        );
      }
    );
    body.append( row );
  }

  for( var key in data )
  {
    var value = data[ key ] ;
    var row = $( '<tr><td>' + key + '</td><td>' + data[ key ] + '</td></tr>' );
    if( typeof value === 'string' && value.startsWith( '/api/v1/' ) )
    {
      row.find( 'td:last' ).on( 'click', function() { $( '#object-detail-dialog' ).modal( 'hide' ); contractor.cinp.get( $( this ).html() ).done( showObject ); } );
    }
    else if( typeof value === 'object' )
    {
      row.find( 'td:last' ).html( '<pre>' + JSON.stringify( value, null, 2 ) + '</pre>' );
    }
    body.append( row );
  }
  $( '#object-detail-dialog' ).modal( 'show' );
}

function showConfig( data, uri )
{
  $( '#object-detail-dialog .modal-title' ).html( 'Full config for ' + uri );
  var body = $( '#object-detail-dialog .modal-body tbody' );
  body.empty();

  for( var key in data )
  {
    var value = data[ key ] ;
    var row = $( '<tr><td>' + key + '</td><td>' + data[ key ] + '</td></tr>' );
     if( typeof value === 'object' )
    {
      row.find( 'td:last' ).html( '<pre>' + JSON.stringify( value, null, 2 ) + '</pre>' );
    }
    body.append( row );
  }
  $( '#object-detail-dialog' ).modal( 'show' );
}

function handleHashChange( event )
{
  const panel_list = [ 'overview', 'blueprints', 'foundations', 'structures', 'jobs' ];
  var panel;

  for( panel of panel_list )
  {
    $( '#' + panel + '-label' ).removeClass( 'active' );
    $( '#' + panel + '-panel' ).hide();
  }

  panel = location.hash;
  if( panel === '' )
  {
    panel = 'overview';
  }
  else
  {
    panel = panel.substr( 1 );
  }

  $( '#' + panel + '-label' ).addClass( 'active' );
  $( '#' + panel + '-panel' ).show();
}

function serverError( message, detail )
{
  $( '#server-error-dialog .modal-body' ).html( message );
  if( detail !== undefined )
  {
    $( '#server-error-dialog .modal-detail' ).html( '<pre>' + detail + '</pre>' );
  }
  else
  {
    $( '#server-error-dialog .modal-detail' ).empty();
  }
  $( '#server-error-dialog' ).modal( 'show' );
}
