import React from 'react';
import { Layout, NavDrawer, Panel, Sidebar, Chip, FontIcon, AppBar, Navigation, Link, Button } from 'react-toolbox';
import SiteSelector from './SiteSelector';

const actions = [
  { label: 'Home', icon: 'home' },
  { label: 'Foundations', icon: 'storage' },
  { label: 'Structures', icon: 'account_balance' },
  { label: 'Networks', icon: 'compare_arrows' },
  { label: 'Jobs', icon: 'dvr' },
];

class NavFrame extends React.Component
{
  state = {
      leftDrawerVisable: true
  };

  menuClick = () =>
  {
    this.setState( { leftDrawerVisable: !this.state.leftDrawerVisable} );
  }

  setSites = ( site_map ) =>
  {
    this.SiteSelector.setSites( site_map );
  }

  render()
  {
    return (
<Layout>
  <NavDrawer pinned={this.state.leftDrawerVisable}>
    <Navigation type='vertical' actions={actions}/>
  </NavDrawer>
  <Panel>
    <AppBar title="Contractor" leftIcon="menu" rightIcon="face" onLeftIconClick={this.menuClick}>
      <Chip><SiteSelector onSiteChange={this.props.onSiteChange}/></Chip>
      <Chip><FontIcon title='Jobs' value='dvr' /> 0</Chip>
      <Chip><FontIcon value='announcement' /> 0</Chip>
      <Button icon='sync' onClick={this.props.onConnect}/>
      <Button icon='update' disabled />
      <Button icon='settings' disabled />
    </AppBar>
  </Panel>
</Layout>
);
  }
};

export default NavFrame;
