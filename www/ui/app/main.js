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

function updateSiteList( id_list, position, count, total )
{
  var foundation_dd = $( '#site-foundation-dropdown' );
  var structure_dd = $( '#site-structure-dropdown' );

  foundation_dd.empty();
  structure_dd.empty();

  for( site_id of id_list )
  {
    foundation_dd.append( $( '<li>' + site_id + '</li>' ).on( 'click', setFoundationSite ).data( 'site', site_id ) );
    structure_dd.append( $( '<li>' + site_id + '</li>' ).on( 'click', setStructureSite ).data( 'site', site_id ) );
  }
}

function setFoundationSite( event )
{
  var element = $( this );

  contractor.getFoundationList( element.data( 'site' ) ).done( updateFoundationTable ).fail( function( message ) { alert( 'Error loading foundations "' + message + '"' ); } );
}

function setStructureSite( event )
{
  var element = $( this );

  contractor.getStructureList( element.data( 'site' ) ).done( updateStructureTable ).fail( function( message ) { alert( 'Error loading structures "' + message + '"' ); } );
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
