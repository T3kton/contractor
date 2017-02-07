var contractorBuilder = {};
(
  function()
  {
    "use strict";

    contractorBuilder = function( cinp )
    {
      var contractor = { cinp: cinp };

      contractor.login = function( username, password )
      {
        var deferred = $.Deferred();

        $.when( this.cinp.call( '/api/v1/User/Session(login)', { 'username': username, 'password': password } ) )
          .then(
            function( result )
            {
              deferred.resolve( result.data );
            }
          )
          .fail(
            function( reason )
            {
              deferred.reject( reason );
            }
          );

        return deferred.promise();
      };

      contractor.logout = function() {};
      contractor.keepalive = function() {};

      contractor.getSiteList = function()
      {
        return this.cinp.list( '/api/v1/Site/Site', undefined, undefined, 0, 100 ); // figure out a way to deal with lots of sites when there are more than 100
      }

      contractor.getFoundationList = function( site )
      {
        return this.cinp.list( '/api/v1/Building/Foundation', 'site', { 'site': site }, 0, 100 );
      }

      contractor.getStructureList = function( site )
      {
        return this.cinp.list( '/api/v1/Building/Structure', 'site', { 'site': site }, 0, 100 );
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
