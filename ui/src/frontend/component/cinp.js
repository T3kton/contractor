/*
 * CInP react client
 * version 0.9
 * for CInP API version 0.9
 *
 * Copyright Peter Howe, Floyd Arguello
 * Released under the Apache 2.0 license
 *
 * Last modified 2017-07-12
 */

const uriRegex = /^(\/([a-zA-Z0-9\-_.!~*]+\/)*)([a-zA-Z0-9\-_.!~*]+)?(:([a-zA-Z0-9\-_.!~*\']*:)*)?(\([a-zA-Z0-9\-_.!~*]+\))?$/;

class CInP
{
  constructor( host )
  {
    this.host = host;
    this.auth_id = null;
    this.auth_token = null;
    this.server_error_handler = null;
  }

  _server_error_handler = ( data ) =>
  {
    if( typeof( data ) === 'object' )
    {
      if( this.server_error_handler !== null )
      {
        this.server_error_handler( data.message, data.trace );
      }
      else
      {
        console.error( 'cinp: Server Error: "' + data.message + '"' );
      }
    }
    else
    {
      if( this.server_error_handler !== null )
      {
        this.server_error_handler( '', data );
      }
      else
      {
        console.error( 'cinp: Server Error: "' + data + '"' );
      }
    }
  };

  _request = ( method, uri, data, header_map ) =>
  {
    if( this.auth_id !== null )
    {
      header_map = Object.assign( {}, header_map, { 'Auth-Id': this.auth_id, 'Auth-Token': this.auth_token } );
    }

    const encodedData = JSON.stringify( data );
    const request = {
      method: method,
      headers: Object.assign( {}, header_map, {
                                                'Accept': 'application/json',
                                                'CInP-Version': '0.9'
                                              } )
    };

    if( encodedData !== undefined )
    {
      request.headers[ 'Content-Length'] = encodedData.length.toString();
      request.headers[ 'Content-Type' ] = 'application/json';
      request.body = encodedData;
    }

    return new Promise( ( resolve, reject ) =>
    {
      fetch( this.host + uri, request ).then(
        ( response ) =>
        {
          if ( response.status < 200 || response.status >= 300 )
          {
            this._ajax_fail( method, uri, reject, response );
          }
          else
          {
            response.text()
              .then( ( data ) =>
              {
                if( data )
                {
                  data = JSON.parse( data );
                }
                else
                {
                  data = null;
                }
                resolve( { data: data, status: response.status, headers: response.headers } );
              }, ( error ) => this._ajax_fail( method, uri, reject, error ) );
          }
        },
        ( error ) =>
        {
          this._ajax_fail( method, uri, reject, error );
        }
      ).catch( ( err ) =>
        {
          console.error( 'cinp: error handeling result: "'+ err + '"' );
          reject( 'Error handeling response' );
        } )
    } );
  };

  _ajax_fail = ( method, uri, reject, response ) =>
  {
    if( !( response instanceof Response ) )
    {
      console.error( 'cinp: doing "' + method + '" on "' +  uri + '" Error: ' + response );
      reject( 'Error "' + response + '"' );
      return;
    }

    console.error( 'cinp: doing "' + method + '" on "' +  uri + '" Status: ' + response.status );

    response.text().then( ( value ) => this._ajax_fail_inner( response, value, reject ) );
  };

  _ajax_fail_inner = ( response, data, reject ) =>
  {
    try
    {
      data = JSON.parse( data );
    }
    finally
    {
      // nothing
    }
    if( response.status == 400 )
    {
      if( typeof( data ) === 'object' )
      {
        if( 'message' in data )
        {
          reject( { reason: 'Invalid Request', detail: data.message } );
        }
        else
        {
          reject( { reason: 'Invalid Request', detail: data } );
        }
      }
      else
      {
        reject( { reason: 'Invalid Request', detail: data } );
      }
    }
    else if( response.status == 401 )
    {
      reject( { reason: 'Invalid Session' } );
    }
    else if( response.status == 403 )
    {
      reject( { reason: 'Not Authorized' } );
    }
    else if( response.status == 404 )
    {
      reject( { reason: 'Not Found' } );
    }
    else if( response.status == 500 )
    {
      this._server_error_handler( data );
      reject( { reason: 'Server Error' } );
    }
    else
    {
      reject( { reason: data } );
    }
  };

  setAuth = ( auth_id, auth_token ) =>
  {
    if( auth_token === undefined || auth_token === '' )
    {
      this.auth_id = null;
      this.auth_token = null;
    }
    else
    {
      this.auth_id = auth_id;
      this.auth_token = auth_token;
    }
  };

  describe = ( uri )=>
  {
    console.info( 'Describe: "' + uri + '"' )

    return this._request( 'DESCRIBE', uri )
      .then( ( result ) =>
        {
          var type = result.headers.get( 'Type' );
          var data = result.data;

          if( type == 'Namespace' )
          {
            return( { type: 'namespace', name: data.name, doc: data.doc, path: data.path, version: data[ 'api-version' ], uri_max: data[ 'multi-uri-max' ], namespace_list: data.namespaces, model_list: data.models } );
          }
          else if( type == 'Model' )
          {
            return( { type: 'model', name: data.name, doc: data.doc, path: data.path, constant_list: data.constants, field_list: data.fields, action_list: data.actions, not_allowed_methods: data[ 'not-allowed-metods' ], list_filters: data[ 'list-filters' ] } );
          }
          else if( type == 'Action' )
          {
            return( { type: 'model', name: data.name, doc: data.doc, path: data.path, return_type: data[ 'return-type' ], static: data.static, paramaters: data.paramaters } );
          }
          else
          {
            console.warn( 'cinp: Unknown type in Discover response "' + type + '"' );
            return( {} );
          }
        }
      );
  };

  get = ( uri, force_multi_mode ) =>
  {
    console.info( 'Get: "' + uri + '"' )

    if( force_multi_mode === undefined )
    {
      force_multi_mode = false;
    }

    return this._request( 'GET', uri, undefined, { 'Multi-Object': force_multi_mode } )
      .then( ( result ) =>
        {
          return ( { data: result.data, multiObject: result.headers.get( 'Multi-Object' ) } );
        }
      );
  };

  create = ( uri, values ) =>
  {
    console.info( 'Create: "' + uri + '"' )

    return this._request( 'CREATE', uri, values )
      .then( ( result ) =>
        {
          return( { data: result.data, id: result.headers.get( 'Object-Id' ) } );
        }
      );
  };

  update = ( uri, values, force_multi_mode ) =>
  {
    console.info( 'Update: "' + uri + '"' )
    if( force_multi_mode === undefined )
    {
      force_multi_mode = false;
    }

    return this._request( 'UPDATE', uri, values, { 'Multi-Object': force_multi_mode } )
     .then( ( result ) =>
        {
          return( { data: result.data, multiObject: result.headers.get( 'Multi-Object' ) } );
        }
      );
  };

  delete = ( uri ) =>
  {
    console.info( 'Delete: "' + uri + '"' )

    return this._request( 'DELETE', uri )
      .then( ( result ) =>
        {
          return( true );
        }
      );
  };

  list = ( uri, filter_name, filter_value_map, position, count ) =>
  {
    console.info( 'List: "' + uri + '"' )
    var args = {};

    if( filter_name !== undefined && filter_name !== '' )
    {
      args.Filter = filter_name;
    }

    if( position !== undefined && position !== '' )
    {
      args.Position = position;
    }

    if( count !== undefined && count !== '' )
    {
      args.Count = count;
    }

    return this._request( 'LIST', uri, filter_value_map, args )
      .then( ( result ) =>
        {
          return( { data: result.data, position: result.headers.get( 'Position' ), count: result.headers.get( 'Count' ), total: result.headers.get( 'Total' ) } );
        }
      );
  };

  call = ( uri, paramater_map, force_multi_mode ) =>
  {
    if( force_multi_mode === undefined )
    {
      force_multi_mode = false;
    }

    return this._request( 'CALL', uri, paramater_map, { 'Multi-Object': force_multi_mode } )
      .then( ( result ) =>
        {
          return( { data: result.data, multiObject: result.headers.get( 'Multi-Object' ) } );
        }
      )
  };

  splitURI = ( uri ) =>
  {
    var parts = uriRegex.exec( uri );

    var result = { namespace: parts[1], model: parts[3], action: undefined, id_list: undefined }
    if( parts[6] !== undefined )
    {
      result.action = parts[6].substr( 1, -1 );
    }
    if( parts[4] !== undefined )
    {
      result.id_list = parts[4].split( ':' );
    }

    return result;
  };

  getMulti = ( uri, id_list, chunk_size ) =>
  {
    if( chunk_size === undefined )
    {
      chunk_size = 10;
    }

    var uri_parts = this.splitURI( uri );

    if( id_list.length == 0 )
    {
      return new Promise( ( resolve, reject ) => resolve( {} ) );
    }
    else
    {
      return this.get( uri_parts.namespace + uri_parts.model + ':' + id_list.join( ':' ) + ':', true );
    }
  };

  static extractIds = ( uri_list ) =>
  {
    var result = [];
    if( !Array.isArray( uri_list ) )
    {
      uri_list = [ uri_list ];
    }

    for( var uri of uri_list )
    {
      if( uri === undefined || uri === null )
        continue;

      var parts = uriRegex.exec( uri );
      if( parts[4] === undefined )
      {
        continue;
      }

      result = result.concat( parts[4].split( ':' ).slice( 1, -1 ) );
    }

    return result;
  }

  // For now we are only getting one list_chunk_size, and getting the all the list at the same time.
  getFilteredObjects = ( uri, filter_name, filter_value_map, list_chunk_size, get_chunk_size ) =>
  {
    if( list_chunk_size === undefined || list_chunk_size === '' )
    {
      list_chunk_size = 100;
    }
    if( get_chunk_size === undefined || get_chunk_size === '' ) // techinically ignored for right now
    {
      get_chunk_size = 10;
    }

    return this.list( uri, filter_name, filter_value_map, 0, list_chunk_size )
      .then( ( result ) =>
      {
        var id_list = CInP.extractIds( result.data );

        return this.getMulti( uri, id_list, result.count );
      } );
  }
}

export default CInP;
