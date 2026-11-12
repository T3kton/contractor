export const dateStr = ( d: any ): string => d instanceof Date ? d.toTimeString() : String( d || '' );

export const configValues = ( obj: any ): [string, string][] =>
  Object.entries( obj || {} ).map( ( [ key, value ] ) => [ key, JSON.stringify( value ) ] as [string, string] );

// names that hold secrets, this should match contractor/Records/lib.py - prepConfig and
// subcontractor/subcontractor/handler.py - _hideify_internal
const SECRET_KEYS = [ 'password', 'token', 'secret' ];

export const isSecret = ( name: string ): boolean => SECRET_KEYS.some( ( i ) => name.includes( i ) );

export interface ModelAttribute {
  name: string;
  value: string;
  secret: boolean;
}

// the type specific attributes of a subclass record: every own property that the base model
// doesn't already have.  Derived rather than listed per type so new plugin fields show up on
// their own.
export const extraAttributes = ( record: any, base: any ): ModelAttribute[] =>
{
  const skip = new Set( [ '_service', ...Object.keys( base ) ] );
  return Object.keys( record )
    .filter( ( name ) => !skip.has( name ) )
    .map( ( name ) => ( { name, value: attrStr( record[ name ] ), secret: isSecret( name ) } ) );
};

// render an arbitrary model attribute for display, the generated model instances stringify to
// their '/api/v1/...' uri, the same as site/blueprint are rendered elsewhere
export const attrStr = ( value: any ): string =>
{
  if ( value === null || value === undefined ) return '';
  if ( value instanceof Date ) return dateStr( value );
  if ( typeof value === 'object' )
  {
    if ( typeof value.toString === 'function' && value.toString !== Object.prototype.toString ) return value.toString();
    return JSON.stringify( value );
  }
  return String( value );
};

export const stateColor = ( state: string ): 'default' | 'success' | 'warning' | 'error' | 'info' =>
{
  switch ( state )
  {
    case 'planned': return 'default';
    case 'built': return 'success';
    case 'located': return 'info';

    case 'done': return 'success';
    case 'waiting': return 'info';
    case 'queued': return 'default';
    case 'paused': return 'warning';
    case 'error': return 'error';
    case 'aborted': return 'warning';

    default: return 'default';
  }
};
