import React from 'react';
import { Dropdown } from 'react-toolbox';

class SiteSelector extends React.Component
{
  state = {
      site_list: [],
      value: null,
  };

  setSites = ( site_map ) => {
    var site_list = [];
    for ( var site in site_map )
    {
      site_list.append( { value: site, label: site_map[ site ].description } );
    }
    self.setState( { site_list: site_list, value: site_list[0].value } );
    this.props.setState( site_list[0].value );
  }

  handleChange = ( value ) => {
    this.setState( { value: value } )
    this.props.onSiteChange( value );
  }

  render()
  {
    return (
<Dropdown title='Current Site' icon='cloud' auto onChange={this.handleChange} source={this.state.site_list} value={this.state.value} allowBlank={false} required={true}/>
);
  }
};

export default SiteSelector;
