import React, { useState, useEffect, useRef } from 'react';
import { useDispatch } from 'react-redux';
import {
  AppBar, Box, Button, Chip, CssBaseline, Dialog, DialogActions,
  DialogContent, DialogTitle, Drawer, IconButton, List, ListItem,
  ListItemButton, ListItemIcon, ListItemText, Menu, MenuItem, TextField, Toolbar, Typography
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import BusinessIcon from '@mui/icons-material/Business';
import MapIcon from '@mui/icons-material/Map';
import RouterIcon from '@mui/icons-material/Router';
import ImportContactsIcon from '@mui/icons-material/ImportContacts';
import StorageIcon from '@mui/icons-material/Storage';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import LocationCityIcon from '@mui/icons-material/LocationCity';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import DvrIcon from '@mui/icons-material/Dvr';
import PublicIcon from '@mui/icons-material/Public';
import ReorderIcon from '@mui/icons-material/Reorder';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import TimelineIcon from '@mui/icons-material/Timeline';
import UpdateIcon from '@mui/icons-material/Update';
import SyncIcon from '@mui/icons-material/Sync';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AnnouncementIcon from '@mui/icons-material/Announcement';
import { BrowserRouter as Router, Routes, Route, useParams, Link as RouterLink } from 'react-router-dom';
import { contractor } from '../store';
import { Site_Site } from '../lib/Contractor';
import { setAuthenticated, showServerError, invalidateAll } from '../store/appSlice';
import type { AppDispatch } from '../store';
import Home from './Home';
import Site from './Site';
import Plot from './Plot';
import Network from './Network';
import Foundation from './Foundation';
import Dependency from './Dependency';
import Structure from './Structure';
import Complex from './Complex';
import BluePrint from './BluePrint';
import PXE from './PXE';
import AddressBlock from './AddressBlock';
import Job from './Job';
import Cartographer from './Cartographer';
import JobLog from './JobLog';
import Todo from './Todo';
import SiteGraph from './SiteGraph';
import SiteSelector from './SiteSelector';
import ServerError from './ServerError';

const DRAWER_WIDTH = 240;

const navItems = [
  { to: '/', icon: <HomeIcon />, label: 'Home' },
  { to: '/sites', icon: <BusinessIcon />, label: 'Sites' },
  { to: '/plots', icon: <MapIcon />, label: 'Plots' },
  { to: '/networks', icon: <RouterIcon />, label: 'Networks' },
  { to: '/blueprints', icon: <ImportContactsIcon />, label: 'BluePrints' },
  { to: '/pxes', icon: <ImportContactsIcon />, label: 'PXEs' },
  { to: '/foundations', icon: <StorageIcon />, label: 'Foundations' },
  { to: '/dependencies', icon: <GroupWorkIcon />, label: 'Dependencies' },
  { to: '/structures', icon: <AccountBalanceIcon />, label: 'Structures' },
  { to: '/complexes', icon: <LocationCityIcon />, label: 'Complexes' },
  { to: '/addressblocks', icon: <CompareArrowsIcon />, label: 'Address Blocks' },
  { to: '/jobs', icon: <DvrIcon />, label: 'Jobs' },
  { to: '/cartographer', icon: <PublicIcon />, label: 'Cartographer' },
  { to: '/joblog', icon: <ReorderIcon />, label: 'Job Log' },
  { to: '/todo', icon: <CheckBoxIcon />, label: 'Todo' },
  { to: '/graph', icon: <TimelineIcon />, label: 'Graph' },
];

function DetailRoute( { Comp, ...extraProps }: { Comp: React.ElementType; [key: string]: unknown } )
{
  const { id } = useParams<{ id: string }>();
  return <Comp id={ id } { ...extraProps } />;
}

const App: React.FC = () =>
{
  const dispatch = useDispatch<AppDispatch>();
  const [curSite, setCurSite] = useState<string | null>( null );
  const [loginVisible, setLoginVisible] = useState( false );
  const [username, setUsername] = useState( '' );
  const [password, setPassword] = useState( '' );
  const [drawerOpen, setDrawerOpen] = useState( true );
  const [autoUpdate, setAutoUpdate] = useState( false );
  const [curJobs, setCurJobs] = useState( 0 );
  const [alerts, setAlerts] = useState( 0 );
  const [loggedInUser, setLoggedInUser] = useState<string | null>( null );
  const [logoutMenuAnchor, setLogoutMenuAnchor] = useState<HTMLElement | null>( null );
  const timerRef = useRef<ReturnType<typeof setInterval> | null>( null );

  const doUpdate = ( site: string | null = curSite ) =>
  {
    dispatch( invalidateAll() );
    if ( site )
    {
      contractor.Foreman_BaseJob_call_jobStats( new Site_Site( contractor, site ) )
        .then( ( result: any ) => { setCurJobs( result.running ?? 0 ); setAlerts( result.error ?? 0 ); } )
        .catch( ( err: any ) => { console.error( 'doUpdate: failed to get job stats:', err?.msg ?? err ); } );
    }
  };

  useEffect( () =>
  {
    contractor.setServerErrorHandler( ( msg: string, trace: string ) =>
    {
      dispatch( showServerError( { msg, trace } ) );
    } );

    const savedId = localStorage.getItem( 'auth-id' );
    const savedToken = localStorage.getItem( 'auth-token' );
    if ( savedId && savedToken )
    {
      contractor.setHeader( 'Auth-Id', savedId );
      contractor.setHeader( 'Auth-Token', savedToken );
      dispatch( setAuthenticated( true ) );
      setLoggedInUser( savedId );
    }

    return () => { if ( timerRef.current ) clearInterval( timerRef.current ); };
  }, [] );

  const selectSite = ( site: string ) =>
  {
    setCurSite( site );
    doUpdate( site );
  };

  const doLogin = () =>
  {
    contractor.Auth_User_call_login( username, password )
      .then( ( token: string ) =>
      {
        contractor.setHeader( 'Auth-Id', username );
        contractor.setHeader( 'Auth-Token', token );
        localStorage.setItem( 'auth-id', username );
        localStorage.setItem( 'auth-token', token );
        dispatch( setAuthenticated( true ) );
        setLoginVisible( false );
        setPassword( '' );
        setLoggedInUser( username );
        doUpdate();
      },
      ( err: any ) => { alert( 'Error logging in: "' + ( err?.msg ?? err ) + '"' ); } );
  };

  const doLogout = () =>
  {
    if ( timerRef.current ) { clearInterval( timerRef.current ); timerRef.current = null; }
    setAutoUpdate( false );
    contractor.clearHeader( 'Auth-Id' );
    contractor.clearHeader( 'Auth-Token' );
    localStorage.removeItem( 'auth-id' );
    localStorage.removeItem( 'auth-token' );
    dispatch( setAuthenticated( false ) );
    setLoggedInUser( null );
    setLogoutMenuAnchor( null );
    setCurSite( null );
    dispatch( invalidateAll() );
  };

  const toggleAutoUpdate = () =>
  {
    if ( autoUpdate )
    {
      if ( timerRef.current ) { clearInterval( timerRef.current ); timerRef.current = null; }
      setAutoUpdate( false );
    }
    else
    {
      timerRef.current = setInterval( () => doUpdate(), 10000 );
      setAutoUpdate( true );
    }
  };

  return (
<Router>
  <Box sx={{ display: 'flex' }}>
    <CssBaseline />
    <ServerError />

    <Dialog open={ loginVisible } onClose={ () => setLoginVisible( false ) }>
      <DialogTitle>Login</DialogTitle>
      <DialogContent>
        <TextField
          type="text"
          label="Username"
          name="username"
          value={ username }
          onChange={ (e) => setUsername( e.target.value ) }
          fullWidth
          margin="dense"
        />
        <TextField
          type="password"
          label="Password"
          name="password"
          value={ password }
          onChange={ (e) => setPassword( e.target.value ) }
          fullWidth
          margin="dense"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={ () => setLoginVisible( false ) }>Close</Button>
        <Button onClick={ doLogin } variant="contained">Login</Button>
      </DialogActions>
    </Dialog>

    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <IconButton color="inherit" edge="start" onClick={ () => setDrawerOpen( !drawerOpen ) } sx={{ mr: 1 }}>
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" sx={{ mr: 2 }}>Contractor</Typography>
        <SiteSelector key={ loggedInUser || 'none' } onSiteChange={ selectSite } curSite={ curSite } />
        <Box sx={{ flexGrow: 1 }} />
        <Chip icon={ <DvrIcon /> } label={ curJobs } title="Jobs" sx={{ mr: 1, color: 'white', borderColor: 'white' }} variant="outlined" />
        <Chip icon={ <AnnouncementIcon /> } label={ alerts } title="Alerts" sx={{ mr: 1, color: 'white', borderColor: 'white' }} variant="outlined" />
        <IconButton color={ autoUpdate ? 'secondary' : 'inherit' } onClick={ toggleAutoUpdate } title="Auto Update">
          <UpdateIcon />
        </IconButton>
        <IconButton color="inherit" onClick={ () => doUpdate() } title="Refresh">
          <SyncIcon />
        </IconButton>
        { loggedInUser
          ? <>
              <Chip
                icon={ <AccountCircleIcon /> }
                label={ loggedInUser }
                onClick={ (e) => setLogoutMenuAnchor( e.currentTarget ) }
                sx={{ color: 'white', borderColor: 'white' }}
                variant="outlined"
              />
              <Menu
                anchorEl={ logoutMenuAnchor }
                open={ Boolean( logoutMenuAnchor ) }
                onClose={ () => setLogoutMenuAnchor( null ) }
              >
                <MenuItem onClick={ doLogout }>Logout</MenuItem>
              </Menu>
            </>
          : <IconButton color="inherit" onClick={ () => setLoginVisible( true ) } title="Login">
              <AccountCircleIcon />
            </IconButton>
        }
      </Toolbar>
    </AppBar>

    <Drawer
      variant="persistent"
      open={ drawerOpen }
      sx={{
        width: drawerOpen ? DRAWER_WIDTH : 0,
        flexShrink: 0,
        transition: 'width 0.2s',
        '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <List dense>
        { navItems.map( ( item ) => (
          <ListItem key={ item.to } disablePadding>
            <ListItemButton component={ RouterLink } to={ item.to }>
              <ListItemIcon>{ item.icon }</ListItemIcon>
              <ListItemText primary={ item.label } />
            </ListItemButton>
          </ListItem>
        ) ) }
      </List>
    </Drawer>

    <Box component="main" sx={{ flexGrow: 1, minWidth: 0, p: 2 }}>
      <Toolbar />
      <Routes>
        <Route path="/" element={ <Home /> } />
        <Route path="/site/:id" element={ <DetailRoute Comp={ Site } /> } />
        <Route path="/plot/:id" element={ <DetailRoute Comp={ Plot } /> } />
        <Route path="/blueprint/f/:id" element={ <DetailRoute Comp={ BluePrint } blueprintType="foundation" /> } />
        <Route path="/blueprint/s/:id" element={ <DetailRoute Comp={ BluePrint } blueprintType="structure" /> } />
        <Route path="/network/:id" element={ <DetailRoute Comp={ Network } /> } />
        <Route path="/pxe/:id" element={ <DetailRoute Comp={ PXE } /> } />
        <Route path="/foundation/:id" element={ <DetailRoute Comp={ Foundation } /> } />
        <Route path="/dependency/:id" element={ <DetailRoute Comp={ Dependency } /> } />
        <Route path="/structure/:id" element={ <DetailRoute Comp={ Structure } /> } />
        <Route path="/complex/:id" element={ <DetailRoute Comp={ Complex } /> } />
        <Route path="/addressblock/:id" element={ <DetailRoute Comp={ AddressBlock } /> } />
        <Route path="/job/f/:id" element={ <DetailRoute Comp={ Job } jobType="foundation" /> } />
        <Route path="/job/s/:id" element={ <DetailRoute Comp={ Job } jobType="structure" /> } />
        <Route path="/job/d/:id" element={ <DetailRoute Comp={ Job } jobType="dependency" /> } />
        <Route path="/sites" element={ <Site /> } />
        <Route path="/plots" element={ <Plot /> } />
        <Route path="/networks" element={ <Network site={ curSite ?? undefined } /> } />
        <Route path="/blueprints" element={ <BluePrint /> } />
        <Route path="/pxes" element={ <PXE site={ curSite ?? undefined } /> } />
        <Route path="/foundations" element={ <Foundation site={ curSite ?? undefined } /> } />
        <Route path="/dependencies" element={ <Dependency site={ curSite ?? undefined } /> } />
        <Route path="/structures" element={ <Structure site={ curSite ?? undefined } /> } />
        <Route path="/complexes" element={ <Complex site={ curSite ?? undefined } /> } />
        <Route path="/addressblocks" element={ <AddressBlock site={ curSite ?? undefined } /> } />
        <Route path="/jobs" element={ <Job site={ curSite ?? undefined } /> } />
        <Route path="/cartographer" element={ <Cartographer /> } />
        <Route path="/joblog" element={ <JobLog site={ curSite ?? undefined } /> } />
        <Route path="/todo" element={ <Todo site={ curSite ?? undefined } /> } />
        <Route path="/graph" element={ <SiteGraph site={ curSite ?? undefined } /> } />
      </Routes>
    </Box>
  </Box>
</Router>
  );
};

export default App;
