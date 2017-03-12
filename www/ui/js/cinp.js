/*
 * CInP jquery client
 * version 0.9
 * for CInP API version 0.9
 *
 * Copyright Peter Howe, Floyd Arguello
 * Released under the Apache 2.0 license
 *
 * Last modified 2016-03-09
 */

var cinpBuilder = {};
(
  function()
  {
    "use strict";

    const uriRegex = /^(\/([a-zA-Z0-9\-_.!~*]+\/)*)([a-zA-Z0-9\-_.!~*]+)?(:([a-zA-Z0-9\-_.!~*\']*:)*)?(\([a-zA-Z0-9\-_.!~*]+\))?$/;

    cinpBuilder = function( host )
    {
      var cinp = { host: host, auth_id: null, auth_token: null, server_error_handler: null };

      cinp._server_error_handler = function( data )
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

      cinp._request = function( method, uri, data, header_map )
      {
        if( this.auth_id !== null )
        {
          header_map = $.extend( {}, header_map, { 'Auth-Id': this.auth_id, 'Auth-Token': this.auth_token } );
        }

        var request = {
          type: method,
          url: this.host + uri,
          dataType: 'json',
          accepts: { json: 'application/json', text: 'application/json' },
          headers: $.extend( {}, header_map, { 'CInP-Version': '0.9' } ),
          data: JSON.stringify( data ),
          contentType: 'application/json',
          processData: false,
          global: false
        };

        if( method == 'DELETE' || method == 'CALL' )
        {
          // server sends empty response on delete, dataType = json it tires to parse the  response, which fails
          // so we set it to text so it dosen't try to parse anything.  which causes us to have to tweek accepts.
          // also Call may return blank
          request.dataType = 'text';
        }

        return $.ajax( request );
      }

      cinp._ajax_fail = function( method, uri, deferred, xhr )
      {
        console.error( 'cinp: doing "' + method + '" on "' +  uri + '" Status: ' + xhr.status );
        var data;
        try
        {
          data = xhr.responseJSON;
        }
        catch( e )
        {
          data = xhr.responseText;
        }

        if( data === undefined ) // for some methods we set dataType to text, for thoes we are going to try to parse the JSON our selves
        {
          data = xhr.responseText;
          try
          {
            var tmp = JSON.parse( data );
          }
          catch( e )
          {
            tmp = data;
          }
          data = tmp;
        }

        if( xhr.status == 0 || ( xhr.status >= 200 && xhr.status < 300 ) )
        {
          deferred.reject( 'Communications Error' ); // This should not happen, usually means there is something wrong with cinp.js, or CORS
        }
        else if( xhr.status == 400 )
        {
          if( typeof( data ) === 'object' )
          {
            if( 'message' in data )
            {
              deferred.reject( 'Invalid Request', data.message );
            }
            else
            {
              deferred.reject( 'Invalid Request', data );
            }
          }
          else
          {
            deferred.reject( 'Invalid Request', data );
          }
        }
        else if( xhr.status == 401 )
        {
          deferred.reject( 'Invalid Session' );
        }
        else if( xhr.status == 403 )
        {
          deferred.reject( 'Not Authorized' );
        }
        else if( xhr.status == 404 )
        {
          deferred.reject( 'Not Found' );
        }
        else if( xhr.status == 500 )
        {
          this._server_error_handler( data );
          deferred.reject( 'Server Error' );
        }
        else
        {
          deferred.reject( data );
        }
      }

      cinp.setAuth = function( auth_id, auth_token )
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

      cinp.describe = function( uri )
      {
        var deferred = $.Deferred();

        console.info( 'Describe: "' + uri + '"' )

        var request = this._request( 'DESCRIBE', uri );

        request
          .done(
            function( data, status, xhr )
            {
              var type = xhr.getResponseHeader( 'Type' );

              if( type == 'Namespace' )
              {
                deferred.resolve( { type: 'namespace', name: data.name, doc: data.doc, path: data.path, version: data[ 'api-version' ], uri_max: data[ 'multi-uri-max' ], namespace_list: data.namespaces, model_list: data.models }, uri );
              }
              else if( type == 'Model' )
              {
                deferred.resolve( { type: 'model', name: data.name, doc: data.doc, path: data.path, constant_list: data.constants, field_list: data.fields, action_list: data.actions, not_allowed_methods: data[ 'not-allowed-metods' ], list_filters: data[ 'list-filters' ] }, uri );
              }
              else if( type == 'Action' )
              {
                deferred.resolve( { type: 'model', name: data.name, doc: data.doc, path: data.path, return_type: data[ 'return-type' ], static: data.static, paramaters: data.paramaters }, uri );
              }
              else
              {
                console.warn( 'cinp: Unknown type in Discover response "' + type + '"' );
                deferred.resolve( {}, uri );
              }
            }
          )
          .fail( function( xhr ) { this._ajax_fail( 'Describe', uri, deferred, xhr ); }.bind( this ) );

        return deferred.promise();
      };

      cinp.get = function( uri, force_multi_mode )
      {
        var deferred = $.Deferred();

        console.info( 'Get: "' + uri + '"' )

        if( force_multi_mode === undefined )
        {
          force_multi_mode = false;
        }

        var request = this._request( 'GET', uri, undefined, { 'Multi-Object': force_multi_mode } );

        request
          .done(
            function( data, status, xhr )
            {
              deferred.resolve( data, xhr.getResponseHeader( 'Multi-Object' ), uri );
            }
          )
          .fail( function( xhr ) { this._ajax_fail( 'Get', uri, deferred, xhr ); }.bind( this ) );

        return deferred.promise();
      };

      cinp.create = function( uri, values )
      {
        var deferred = $.Deferred();

        console.info( 'Create: "' + uri + '"' )

        var request = this._request( 'CREATE', uri, values );

        request
          .done(
            function( data, status, xhr )
            {
              deferred.resolve( data, xhr.getResponseHeader( 'Object-Id' ) );
            }
          )
          .fail( function( xhr ) { this._ajax_fail( 'Create', uri, deferred, xhr ); }.bind( this ) );

        return deferred.promise();
      };

      cinp.update = function( uri, values, force_multi_mode )
      {
        var deferred = $.Deferred();

        console.info( 'Update: "' + uri + '"' )
        if( force_multi_mode === undefined )
        {
          force_multi_mode = false;
        }

        var request = this._request( 'UPDATE', uri, values, { 'Multi-Object': force_multi_mode } );

        request
          .done(
            function( data, status, xhr )
            {
              deferred.resolve( data, xhr.getResponseHeader( 'Multi-Object' ), uri );
            }
          )
          .fail( function( xhr ) { this._ajax_fail( 'Update', uri, deferred, xhr ); }.bind( this ) );

        return deferred.promise();
      };

      cinp.delete = function( uri )
      {
        var deferred = $.Deferred();

        console.info( 'Delete: "' + uri + '"' )

        var request = this._request( 'DELETE', uri );

        request
          .done(
            function( data, status, xhr )
            {
              deferred.resolve( uri );
            }
          )
          .fail( function( xhr ) { this._ajax_fail( 'Delete', uri, deferred, xhr ); }.bind( this ) );

        return deferred.promise();
      };

      cinp.list = function( uri, filter_name, filter_value_map, position, count )
      {
        var deferred = $.Deferred();

        console.info( 'List: "' + uri + '"' )
        if( position === undefined || position === '' )
        {
          position = 0;
        }

        if( count === undefined || count === '' )
        {
          count = 10;
        }

        var request = this._request( 'LIST', uri, filter_value_map, { Position: position, Count: count, Filter: filter_name } );

        request
          .done(
            function( data, status, xhr )
            {
              deferred.resolve( data, xhr.getResponseHeader( 'Position' ), xhr.getResponseHeader( 'Count' ), xhr.getResponseHeader( 'Total' ), uri );
            }
          )
          .fail( function( xhr ) { this._ajax_fail( 'List', uri, deferred, xhr ); }.bind( this ) );

        return deferred.promise();
      };

      cinp.call = function( uri, paramater_map, force_multi_mode )
      {
        var deferred = $.Deferred();

        if( force_multi_mode === undefined )
        {
          force_multi_mode = false;
        }

        var request = this._request( 'CALL', uri, paramater_map, { 'Multi-Object': force_multi_mode } );

        request
          .done(
            function( data, status, xhr )
            {
              if( data == '' ) // deal with unparsable blank reply
              {
                data = null;
              }
              else
              {
                data = JSON.parse( data );
              }
              deferred.resolve( data, uri );
            }
          )
          .fail( function( xhr ) { this._ajax_fail( 'Call', uri, deferred, xhr ); }.bind( this ) );

        return deferred.promise();
      }

      cinp.splitURI = function( uri )
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
      }

      cinp.extractIds = function( uri_list )
      {
        var result = [];

        for( var uri of uri_list )
        {
          var parts = uriRegex.exec( uri );
          if( parts[4] === undefined )
          {
            continue;
          }

          result = result.concat( parts[4].split( ':' ).slice( 1, -1 ) );
        }

        return result;
      }

      cinp.getMulti = function( uri, id_list, chunk_size )
      {
        if( chunk_size === undefined )
        {
          chunk_size = 10;
        }

        var deferred = $.Deferred();

        var uri_parts = this.splitURI( uri );

        if( id_list.length == 0 )
        {
          deferred.resolve( {} );
        }
        else
        {
          this.get( uri_parts.namespace + uri_parts.model + ':' + id_list.join( ':' ) + ':', true )
            .done( function( data ) { deferred.resolve( data ); } )
            .fail( function() { deferred.reject.apply( deferred, arguments ); } );
        }

        return deferred.promise();
      }

      cinp.getFilteredObjects = function( uri, filter_name, filter_value_map, list_chunk_size, get_chunk_size ) // For now we are only getting one list_chunk_size, and getting the all the list at the same time.
      {
        if( list_chunk_size === undefined )
        {
          list_chunk_size = 100;
        }
        if( get_chunk_size === undefined ) // techinically ignored for right now
        {
          get_chunk_size = 10;
        }

        var deferred = $.Deferred();

        this.list( uri, filter_name, filter_value_map, 0, list_chunk_size )
          .done( function( data, position, count, total ) { return this._getFilteredObjectsDone( deferred, uri, data, position, count, total ); }.bind( this ) )
          .fail( function() { deferred.reject.apply( deferred, arguments ); } );

        return deferred.promise();
      }

      cinp._getFilteredObjectsDone = function( deferred, uri, data, position, count, total )
      {
        var id_list = this.extractIds( data );

        if( id_list.length == 0 )
        {
          deferred.resolve( {} );
        }

        this.getMulti( uri, id_list, count )
          .done( function( object_map ) { deferred.resolve( object_map ); } )
          .fail( function() { deferred.reject.apply( deferred, arguments ); } );
      }

      return cinp;
    };
  }
)();
