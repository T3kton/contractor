import CInP from './cinp';

class Contractor
{
  constructor( host )
  {
    this.authenticated = false;
    this.cinp = new CInP( host );
  };

  login = ( username, password ) =>
  {
    return this.cinp.call( '/api/v1/Auth/User(login)', { 'username': username, 'password': password } );
  };

  logout = () => {};
  keepalive = () => {};

  setAuth = ( username, auth_token ) =>
  {
    if( auth_token === undefined || auth_token === '' )
    {
      this.authenticated = false;
    }
    else
    {
      this.cinp.setAuth( username, auth_token );
      this.authenticated = true;
    }
  };

  getSiteList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Site/Site' ); // figure out a way to deal with lots of sites when there are more than 100
  };

  getPlotList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Survey/Plot' );
  };

  getNetworkList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Utilities/Network', 'site', { 'site': site }  );
  };

  getFoundationList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Foundation', 'site', { 'site': site } );
  };

  getDependencyList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Dependency', 'site', { 'site': site } );
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

  getPXEList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/BluePrint/PXE' );
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

  getDependencyJobList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Foreman/DependencyJob', 'site', { 'site': site } );
  };

  getJobLogList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Foreman/JobLog', 'site', { 'site': site } );
  };

  getCartographerList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Survey/Cartographer' );
  };

  getTodoList = ( site, hasDependancies, foundationClass ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Foundation', 'todo', { 'site': site, 'has_dependancies': hasDependancies, 'foundation_class': foundationClass } );
  };

  getFoundationClassList = () =>
  {
    return this.cinp.call( '/api/v1/Building/Foundation(getFoundationTypes)' )
  };

  getSiteDependencyMap = ( site ) =>
  {
    return this.cinp.call( site + '(getDependencyMap)' );
  };

  getJobStats = ( site ) =>
  {
    return this.cinp.call( '/api/v1/Foreman/BaseJob(jobStats)', { 'site': site } );
  }

  getSite = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Site/Site:' + id + ':' );
  };

  getPlot = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Survey/Plot:' + id + ':' );
  };

  getNetwork = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Utilities/Network:' + id + ':' );
  };


  getNetworkAddressBlockList = ( id ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Utilities/NetworkAddressBlock', 'network', { 'network': '/api/v1/Utilities/Network:' + id + ':' } );
  };

  getFoundation = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Foundation:' + id + ':' );
  };

  getFoundationInterfaces = ( id ) =>
  {
    return this.cinp.call( '/api/v1/Building/Foundation:' + id + ':(getInterfaceList)' );
  }

  getFoundationDependandyList = ( id ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Building/Dependency', 'foundation', { 'foundation': '/api/v1/Building/Foundation:' + id + ':' } );
  };

  getDependency = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Dependency:' + id + ':' );
  };

  getStructure = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Structure:' + id + ':' );
  };

  getStructureAddressList = ( id ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Utilities/Address', 'structure', { 'structure': '/api/v1/Building/Structure:' + id + ':' } );
  };

  getComplex = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Complex:' + id + ':' );
  };

  getFoundationBluePrint = ( id ) =>
  {
    return this.cinp.get( '/api/v1/BluePrint/FoundationBluePrint:' + id + ':' );
  };

  getStructureBluePrint = ( id ) =>
  {
    return this.cinp.get( '/api/v1/BluePrint/StructureBluePrint:' + id + ':' );
  };

  getPXE = ( id ) =>
  {
    return this.cinp.get( '/api/v1/BluePrint/PXE:' + id + ':' );
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

  getJobState = ( uri ) =>
  {
    var variables = this.cinp.call( uri + '(jobRunnerVariables)' );
    var state = this.cinp.call( uri + '(jobRunnerState)' );

    return Promise.all( [ variables, state ] );
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
