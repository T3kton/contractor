import CInP from './cinp';

class Contractor
{
  constructor( host )
  {
    this.cinp = new CInP( host );
  };

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
  };

  logout = () => {};
  keepalive = () => {};

  getSiteList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Site/Site' ); // figure out a way to deal with lots of sites when there are more than 100
  };

  getFoundationList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Foundation', 'site', { 'site': site } );
  };

  getDependancyList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Dependancy', 'site', { 'site': site } );
  };

  getStructureList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Structure', 'site', { 'site': site } );
  };

  getComplexList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Complex', 'site', { 'site': site } );
  };

  getFoundationBluePrintList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/BluePrint/FoundationBluePrint' );
  };

  getStructureBluePrintList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/BluePrint/StructureBluePrint' );
  };

  getAddressBlockList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Utilities/AddressBlock', 'site', { 'site': site } );
  };

  getFoundationJobList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Foreman/FoundationJob', 'site', { 'site': site } );
  };

  getStructureJobList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Foreman/StructureJob', 'site', { 'site': site } );
  };

  getDependancyJobList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Foreman/DependancyJob', 'site', { 'site': site } );
  };

  getTodoList = ( site, isAutoBuild, hasDependancies, foundationClass ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Foundation', 'todo', { 'site': site, 'auto_build': isAutoBuild, 'has_dependancies': hasDependancies, 'foundation_class': foundationClass } );
  };

  getFoundationClassList = () =>
  {
    return this.cinp.call( '/api/v1/Building/Foundation(getFoundationTypes)' )
  };

  getSiteDependancyMap = ( site ) =>
  {
    return this.cinp.call( site + '(getDependancyMap)' );
  };

  getJobStats = ( site ) =>
  {
    return this.cinp.call( '/api/v1/Foreman/BaseJob(jobStats)', { 'site': site } );
  }

  getSite = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Site/Site:' + id + ':' );
  };

  getFoundation = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Foundation:' + id + ':' );
  };

  getFoundationDependandyList = ( id ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Dependancy', 'foundation', { 'foundation': '/api/v1/Building/Foundation:' + id + ':' } );
  };

  getDependancy = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Dependancy:' + id + ':' );
  };

  getStructure = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Structure:' + id + ':' );
  };

  getComplex = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Complex:' + id + ':' );
  };

  getDependancy = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Dependancy:' + id + ':' );
  };

  getFoundationBluePrint = ( id ) =>
  {
    return this.cinp.get( '/api/v1/BluePrint/FoundationBluePrint:' + id + ':' );
  };

  getStructureBluePrint = ( id ) =>
  {
    return this.cinp.get( '/api/v1/BluePrint/StructureBluePrint:' + id + ':' );
  };

  getScript = ( id ) =>
  {
    return this.cinp.get( '/api/v1/BluePrint/Script:' + id + ':' );
  };

  getAddressBlock = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Utilities/AddressBlock:' + id + ':' );
  };

  pauseJob = ( uri ) =>
  {
    return this.cinp.call( uri + '(pause)' );
  };

  resumeJob = ( uri ) =>
  {
    return this.cinp.call( uri + '(resume)' );
  };

  resetJob = ( uri ) =>
  {
    return this.cinp.call( uri + '(reset)' );
  };

  rollbackJob = ( uri ) =>
  {
    return this.cinp.call( uri + '(rollback)' );
  };

  getConfig = ( uri ) =>
  {
    return this.cinp.call( uri + '(getConfig)' );
  };

  getAddressBlockAddresses = ( addressBlockId ) =>
  {
    var full_result = {};

    var addressBlock = '/api/v1/Utilities/AddressBlock:' + addressBlockId + ':';

    return this.cinp.getFilteredObjects( '/api/v1/Utilities/Address', 'address_block', { 'address_block': addressBlock } )
      .then( ( result ) =>
      {
        Object.assign( full_result, result.data );
        return this.cinp.getFilteredObjects( '/api/v1/Utilities/ReservedAddress', 'address_block', { 'address_block': addressBlock } );
      }
      ).then( ( result ) =>
      {
        Object.assign( full_result, result.data );
        return this.cinp.getFilteredObjects( '/api/v1/Utilities/DynamicAddress', 'address_block', { 'address_block': addressBlock } );
      }
      ).then( ( result ) =>
      {
        Object.assign( full_result, result.data );
        return Promise.resolve( full_result );
      } );
  };
}

export default Contractor;
