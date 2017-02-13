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
        return this.cinp.getFilteredObjects( '/api/v1/Site/Site' ); // figure out a way to deal with lots of sites when there are more than 100
      }

      contractor.getFoundationList = function( site )
      {
        return this.cinp.getFilteredObjects( '/api/v1/Building/Foundation', 'site', { 'site': site } );
      }

      contractor.getStructureList = function( site )
      {
        return this.cinp.getFilteredObjects( '/api/v1/Building/Structure', 'site', { 'site': site } );
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
