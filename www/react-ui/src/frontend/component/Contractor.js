import CInP from './cinp';

class Contractor
{
  constructor( host )
  {
    this.cinp = new CInP( host );
  }

  login = () =>
  {
    this.cinp.call( '/api/v1/User/Session(login)', { 'username': username, 'password': password } )
      .then(
        function( result )
        {
          resolve( result.data );
        },
        function( reason )
        {
          reject( reason );
        }
      );
  }

  logout = () => {}
  keepalive = () => {}

  getSiteList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Site/Site' ); // figure out a way to deal with lots of sites when there are more than 100
  }

  getFoundationList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Foundation', 'site', { 'site': site } );
  }

  getStructureList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Structure', 'site', { 'site': site } );
  }

  getAddressBlockList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Utilities/AddressBlock', 'site', { 'site': site } );
  }

  getFoundation = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Foundation:' + id + ':' );
  }
}

/*

      contractor.getAddressBlockAddresses = function( address_block )
      {
        var deferred = $.Deferred();
        var full_result = {};
        var cinp = this.cinp;

        $.when( cinp.getFilteredObjects( '/api/v1/Utilities/Address', 'address_block', { 'address_block': address_block } ) )
          .then(
            function( result )
            {
              $.extend( full_result, result )
              $.when( cinp.getFilteredObjects( '/api/v1/Utilities/ReservedAddress', 'address_block', { 'address_block': address_block } ) )
              .then(
                function( result )
                {
                  $.extend( full_result, result )
                  $.when( cinp.getFilteredObjects( '/api/v1/Utilities/DynamicAddress', 'address_block', { 'address_block': address_block } ) )
                  .then(
                    function( result )
                    {
                      $.extend( full_result, result )
                      deferred.resolve( full_result );
                    }
                  )
                  .fail(
                    function( reason )
                    {
                      deferred.reject( reason );
                    }
                  );
                }
              )
              .fail(
                function( reason )
                {
                  deferred.reject( reason );
                }
              );
            }
          )
          .fail(
            function( reason )
            {
              deferred.reject( reason );
            }
          );

        return deferred.promise();
      }


      contractor.getFoundationJobList = function( site )
      {
        return this.cinp.getFilteredObjects( '/api/v1/Foreman/FoundationJob', 'site', { 'site': site } );
      }

      contractor.getStructureJobList = function( site )
      {
        return this.cinp.getFilteredObjects( '/api/v1/Foreman/StructureJob', 'site', { 'site': site } );
      }

      contractor.getFoundationBluePrints = function()
      {
        var deferred = $.Deferred();

        $.when( this.cinp.getFilteredObjects( '/api/v1/BluePrint/FoundationBluePrint', nil, {} ) ).then();

        return deferred.promise();
      }

      return contractor;
    };
  }
)();
*/

export default Contractor;
