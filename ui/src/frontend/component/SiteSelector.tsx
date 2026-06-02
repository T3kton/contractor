import React, { useEffect, useRef, useState } from 'react';
import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { contractor, store } from '../store';

interface SiteSelectorProps {
  onSiteChange: ( site: string ) => void;
  curSite: string | null;
}

const SiteSelector: React.FC<SiteSelectorProps> = ( { onSiteChange, curSite } ) =>
{
  const [siteList, setSiteList] = useState<{ value: string; label: string }[]>( [] );
  const onSiteChangeRef = useRef( onSiteChange );
  onSiteChangeRef.current = onSiteChange;

  useEffect( () =>
  {
    if ( !store.getState().app.authenticated ) return;

    contractor.Site_Site_get_multi( { filter: undefined } )
      .then( ( result: any ) =>
      {
        const list = Object.values( result ).map( ( site: any ) => ( { value: site.name, label: site.description } ) );
        setSiteList( list );
        if ( list.length > 0 ) onSiteChangeRef.current( list[0].value );
      } )
      .catch( ( err: any ) =>
      {
        console.error( 'SiteSelector: failed to load sites:', err?.msg ?? err );
      } );
  }, [] );

  return (
<FormControl size="small" sx={{ minWidth: 150 }}>
  <InputLabel>Site</InputLabel>
  <Select
    value={ curSite || '' }
    onChange={ (e) => onSiteChange( e.target.value ) }
    label="Site"
  >
    { siteList.map( ( site ) => (
      <MenuItem key={ site.value } value={ site.value }>{ site.label }</MenuItem>
    ) ) }
  </Select>
</FormControl>
  );
};

export default SiteSelector;
