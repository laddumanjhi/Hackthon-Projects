import React from 'react';
import { Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, makeStyles } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  title: {
    flexGrow: 1,
  },
  link: {
    color: 'white',
    textDecoration: 'none',
    marginLeft: theme.spacing(2),
  },
}));

function Navbar() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" className={classes.title}>
            Education Portal
          </Typography>
          <Button color="inherit">
            <Link to="/" className={classes.link}>Dashboard</Link>
          </Button>
          <Button color="inherit">
            <Link to="/courses" className={classes.link}>Courses</Link>
          </Button>
          <Button color="inherit">
            <Link to="/users" className={classes.link}>Users</Link>
          </Button>
        </Toolbar>
      </AppBar>
    </div>
  );
}

export default Navbar; 