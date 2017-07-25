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

  getFoundationBluePrintList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/BluePrint/FoundationBluePrint' );
  }

  getStructureBluePrintList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/BluePrint/StructureBluePrint' );
  }

  getAddressBlockList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Utilities/AddressBlock', 'site', { 'site': site } );
  }

  getFoundationJobList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Foreman/FoundationJob', 'site', { 'site': site } );
  }

  getStructureJobList = ( site ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Foreman/StructureJob', 'site', { 'site': site } );
  }

  getSite = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Site/Site:' + id + ':' );
  }

  getFoundation = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Foundation:' + id + ':' );
  }

  getStructure = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Building/Structure:' + id + ':' );
  }

  getFoundationBluePrint = ( id ) =>
  {
    return this.cinp.get( '/api/v1/BluePrint/FoundationBluePrint:' + id + ':' );
  }

  getStructureBluePrint = ( id ) =>
  {
    return this.cinp.get( '/api/v1/BluePrint/StructureBluePrint:' + id + ':' );
  }

  getAddressBlock = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Utilities/AddressBlock:' + id + ':' );
  }

  getFoundationJob = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Foreman/FoundationJob:' + id + ':' );
  }

  getStructureJob = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Foreman/StructureJob' + id + ':' );
  }

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
  }
}

export default Contractor;
